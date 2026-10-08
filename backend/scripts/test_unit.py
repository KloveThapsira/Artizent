import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import urllib.parse
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_path))

from agents.deploy_agent import deploy_project, netlify_api_deploy
from services.url_extractor import extract_url

class TestDeployAgent(unittest.TestCase):
    
    @patch('agents.deploy_agent.run_command')
    @patch('agents.deploy_agent.requests.get')
    def test_netlify_raw_decode(self, mock_get, mock_run):
        # Mock netlify CLI returning JSON followed by trailing text/ansi escape sequences
        json_data = {
            "url": "https://test-site.netlify.app",
            "deploy_url": "https://deploy-123--test-site.netlify.app"
        }
        mock_run.return_value = (0, json.dumps(json_data) + "\n✔ Deploy is live!\nSome spinner details here...")
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        # Call deploy_project
        platform_data = {
            "recommended_platform": "Netlify",
            "output_folder": "dist"
        }
        
        ok, logs, live = deploy_project(
            root="C:/dummy/project",
            platform_data=platform_data,
            token="dummy-token",
            mode="real"
        )
        
        self.assertTrue(ok)
        self.assertEqual(live, "https://test-site.netlify.app")

    @patch('agents.deploy_agent.requests.Session')
    def test_netlify_api_deploy_list(self, mock_session_class):
        # Test case where Netlify API returns 'required' as a list of SHAs
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock site creation response
        mock_site_resp = MagicMock()
        mock_site_resp.status_code = 201
        mock_site_resp.json.return_value = {"id": "site_123", "ssl_url": "https://test-site.netlify.app"}
        
        # Mock deploy creation response returning list of required SHAs
        mock_deploy_resp = MagicMock()
        mock_deploy_resp.status_code = 201
        mock_deploy_resp.json.return_value = {
            "id": "deploy_123",
            "required": ["sha_abc123"]
        }
        
        mock_session.post.side_effect = [mock_site_resp, mock_deploy_resp]
        
        # Mock file uploads
        mock_put_resp = MagicMock()
        mock_put_resp.status_code = 200
        mock_session.put.return_value = mock_put_resp
        
        # Mock os.walk and file operations
        with patch('os.walk') as mock_walk, \
             patch('builtins.open', mock_open(read_data=b"dummy content")):
            
            mock_walk.return_value = [
                ("/dummy/dist", [], ["index.html"])
            ]
            
            # Mock hashlib.sha1 to return a fixed hash
            with patch('hashlib.sha1') as mock_sha:
                mock_sha_obj = MagicMock()
                mock_sha_obj.hexdigest.return_value = "sha_abc123"
                mock_sha.return_value = mock_sha_obj
                
                ok, logs, live = netlify_api_deploy("/dummy/dist", "dummy-token", "test-site")
                
                self.assertTrue(ok)
                self.assertEqual(live, "https://test-site.netlify.app")
                
                # Verify PUT call with correct URL-encoded path and headers
                expected_url = "https://api.netlify.com/api/v1/deploys/deploy_123/files/index.html"
                mock_session.put.assert_called_once_with(
                    expected_url,
                    data=b"dummy content",
                    headers={"Content-Type": "application/octet-stream"}
                )

    @patch('agents.deploy_agent.run_command')
    @patch('agents.deploy_agent.requests.get')
    def test_railway_deploy_env_and_domain_fallback(self, mock_get, mock_run):
        # Mock railway CLI
        # 1. railway.cmd not found, railway not found, npx @railway/cli succeeds but NO url
        # 2. railway domain fallback via npx outputs url
        call_count = [0]
        def side_effect(args, cwd, token, timeout, env=None):
            call_count[0] += 1
            # Verify both token env vars set
            if env:
                self.assertEqual(env.get("RAILWAY_TOKEN"), "railway-token-123")
                self.assertEqual(env.get("RAILWAY_API_TOKEN"), "railway-token-123")
            # First calls are CLI attempts that fail with "command not found"
            if args[0] in ("railway.cmd", "railway"):
                return (1, "Command not found: railway")
            # npx @railway/cli up --ci succeeds without URL in output
            if "@railway/cli" in args and "up" in args:
                return (0, "Deploying... build complete.")
            # npx @railway/cli domain returns domain
            if "@railway/cli" in args and "domain" in args:
                return (0, "Domain generated: https://my-railway-app.up.railway.app")
            return (1, "Unknown command")

        mock_run.side_effect = side_effect

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        platform_data = {
            "recommended_platform": "Railway",
            "output_folder": ""
        }

        ok, logs, live = deploy_project(
            root="C:/dummy/project",
            platform_data=platform_data,
            token="railway-token-123",
            mode="real"
        )

        self.assertTrue(ok)
        self.assertEqual(live, "https://my-railway-app.up.railway.app")

    @patch('agents.deploy_agent.requests.get')
    def test_verify_live_url_scheme(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        
        platform_data = {
            "recommended_platform": "Netlify",
            "output_folder": "dist"
        }
        
        with patch('agents.deploy_agent.run_command') as mock_run:
            # return a URL without http/https
            mock_run.return_value = (0, '{"url": "my-site.netlify.app"}')
            
            ok, logs, live = deploy_project(
                root="C:/dummy/project",
                platform_data=platform_data,
                token="dummy-token",
                mode="real"
            )
            
            # verify it got prepended with https:// and verified
            mock_get.assert_called_with("https://my-site.netlify.app", timeout=10)
            self.assertTrue(ok)
            self.assertEqual(live, "https://my-site.netlify.app")

    def test_explain_error(self):
        from agents.error_agent import explain_error
        
        credit_err = 'Deploy creation failed: 403 {"error":"Account credit usage exceeded - new deploys are blocked until credits are added"}'
        forbidden_err = 'Error: Forbidden 403'
        
        explanation1 = explain_error(credit_err)
        explanation2 = explain_error(forbidden_err)
        
        self.assertIn("credit", explanation1.lower())
        self.assertIn("forbidden", explanation2.lower())

if __name__ == '__main__':
    unittest.main()
