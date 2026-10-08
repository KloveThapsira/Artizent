import time
import random
import string
from pathlib import Path
from services.command_service import run_command
from services.url_extractor import extract_url
import json
import requests
import hashlib
import os

def netlify_api_deploy(out_dir: str, token: str, project_name: str):
    """Deploy a static site directory to Netlify using the REST API as a fallback when CLI is unavailable.
    This will create a site named after `project_name` (if possible) and upload files.
    Returns (ok: bool, logs: str, live_url: str|None)
    """
    logs = []
    headers = {"Authorization": f"Bearer {token}"}
    session = requests.Session()
    session.headers.update(headers)

    # collect files and sha1 hashes
    file_map = {}
    for root, dirs, files in os.walk(out_dir):
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, out_dir).replace("\\", "/")
            with open(full, "rb") as fh:
                data = fh.read()
            sha = hashlib.sha1(data).hexdigest()
            file_map[rel] = sha

    if not file_map:
        return False, "No files found in output directory for API deploy.", None

    # create site
    try:
        r = session.post("https://api.netlify.com/api/v1/sites", json={"name": project_name})
        if r.status_code in (200, 201):
            site = r.json()
            site_id = site.get("id")
            live_url = site.get("ssl_url") or site.get("url")
            logs.append(f"Created site {site_id} {live_url}")
        else:
            # handle duplicate subdomain (site exists)
            if r.status_code == 422 and "subdomain" in (r.text or "").lower():
                logs.append("Site name already taken; creating unnamed site instead")
                # create site without specifying name to get a unique site
                anon_r = session.post("https://api.netlify.com/api/v1/sites")
                if anon_r.status_code in (200,201):
                    site = anon_r.json()
                    site_id = site.get("id")
                    live_url = site.get("ssl_url") or site.get("url")
                    logs.append(f"Created anonymous site {site_id} {live_url}")
                else:
                    # fallback to listing sites to attempt reuse
                    list_r = session.get("https://api.netlify.com/api/v1/sites")
                    if list_r.status_code == 200:
                        sites = list_r.json()
                        match = None
                        for s in sites:
                            if (s.get("name") or "").lower() == project_name.lower() or project_name.lower() in (s.get("name") or "").lower():
                                match = s
                                break
                        if not match and sites:
                            match = sites[0]
                        if match:
                            site = match
                            site_id = site.get("id")
                            live_url = site.get("ssl_url") or site.get("url")
                            logs.append(f"Using existing site {site_id} {live_url}")
                        else:
                            return False, f"Site creation failed and no existing site found: {r.status_code} {r.text}", None
                    else:
                        return False, f"Site creation failed and listing sites failed: {list_r.status_code} {list_r.text}", None
            else:
                return False, f"Site creation failed: {r.status_code} {r.text}", None
    except Exception as e:
        return False, f"Site creation error: {e}", None

    # create deploy - tell Netlify file SHAs
    try:
        deploy_r = session.post(f"https://api.netlify.com/api/v1/sites/{site_id}/deploys", json={"files": file_map})
        if deploy_r.status_code not in (200, 201):
            return False, f"Deploy creation failed: {deploy_r.status_code} {deploy_r.text}", None
        deploy_obj = deploy_r.json()
        # Netlify returns 'required' mapping of path -> upload_url or list of SHAs
        required = deploy_obj.get("required") or deploy_obj.get("missing") or []
        sha_to_path = {sha: rel for rel, sha in file_map.items()}
        if isinstance(required, list):
            for sha in required:
                rel_path = sha_to_path.get(sha)
                if not rel_path:
                    continue
                full = os.path.join(out_dir, rel_path.replace("/", os.sep))
                try:
                    with open(full, "rb") as fh:
                        import urllib.parse
                        quoted_path = urllib.parse.quote(rel_path)
                        put_r = session.put(
                            f"https://api.netlify.com/api/v1/deploys/{deploy_obj['id']}/files/{quoted_path}",
                            data=fh.read(),
                            headers={"Content-Type": "application/octet-stream"}
                        )
                    if put_r.status_code not in (200, 201):
                        logs.append(f"Upload failed for {rel_path}: {put_r.status_code} {put_r.text}")
                except Exception as e:
                    logs.append(f"Upload exception for {rel_path}: {e}")
        elif isinstance(required, dict):
            for rel_path, upload_url in required.items():
                # upload file content via PUT
                full = os.path.join(out_dir, rel_path.replace("/", os.sep))
                try:
                    with open(full, "rb") as fh:
                        put_r = requests.put(upload_url, data=fh.read(), headers={"Content-Type": "application/octet-stream"})
                    if put_r.status_code not in (200, 201):
                        logs.append(f"Upload failed for {rel_path}: {put_r.status_code}")
                except Exception as e:
                    logs.append(f"Upload exception for {rel_path}: {e}")
        # final live URL may be in deploy_obj
        deploy_url = deploy_obj.get("deploy_ssl_url") or deploy_obj.get("deploy_url") or deploy_obj.get("url")
        if deploy_url:
            return True, "\n".join(logs + [f"Deployed: {deploy_url}"]), deploy_url
        return True, "\n".join(logs + ["Deploy created; no immediate URL available."]), live_url
    except Exception as e:
        return False, f"Deploy creation exception: {e}", None

def fake_url(project_name: str, platform: str):
    slug = "".join(c.lower() if c.isalnum() else "-" for c in project_name).strip("-")[:25] or "project"
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    domains = {
        "Netlify": "netlify.app",
        "Vercel": "vercel.app",
        "Railway": "up.railway.app",
        "Render": "onrender.com",
        "Azure": "azurewebsites.net"
    }
    return f"https://{slug}-{suffix}.{domains.get(platform, 'example.com')}"

def deploy_project(root: str, platform_data: dict, token: str | None = None, mode: str = "simulation", project_id: str = ""):
    path = Path(root)
    platform = platform_data["recommended_platform"]
    project_name = path.name

    if mode == "simulation":
        # Determine the best directory to serve (build output or project root)
        output_folder = platform_data.get("output_folder") or ""
        serve_dir = path
        # Check for common build output folders
        for candidate in [output_folder, "dist", "build", ".next/out", "out", "public"]:
            if candidate and (path / candidate).is_dir():
                serve_dir = path / candidate
                break

        # Check if serve_dir has an index.html; if not fall back to root
        if not (serve_dir / "index.html").exists() and (path / "index.html").exists():
            serve_dir = path

        preview_url = f"http://localhost:8000/preview/{project_id}" if project_id else f"http://localhost:8000/preview/unknown"

        logs = [
            "✅ Simulation mode enabled.",
            f"📦 Selected platform: {platform}",
            f"📂 Serving from: {serve_dir}",
            "🔧 Deployment command prepared safely.",
            "🚀 Local preview server started.",
            f"🌐 Preview URL: {preview_url}",
            "",
            "ℹ️  This is a local preview of your project.",
            "   For real deployment, switch to Real Deployment Mode and enter your platform token."
        ]
        return True, "\n".join(logs), preview_url

    def verify_live_url(url: str, attempts: int = 5, delay: int = 4):
        """Try to GET the URL several times to allow CDN/propagation delays."""
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        for i in range(attempts):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code < 400:
                    return True, None
                # record last status and retry
                last_status = r.status_code
            except Exception as e:
                last_err = e
            time.sleep(delay)
        # failed after retries
        if 'last_status' in locals():
            return False, f"site returned HTTP {last_status} after {attempts} attempts"
        return False, f"unreachable after {attempts} attempts: {last_err}"

    if platform == "Netlify":
        # Determine the best output directory to deploy (prefer build outputs)
        output_folder = platform_data.get("output_folder") or ""
        out_dir_path = path
        for candidate in [output_folder, "dist", "build", ".next/out", "out", "public"]:
            if candidate and (path / candidate).is_dir():
                out_dir_path = path / candidate
                break
        # If the chosen directory doesn't have index.html but root does, fall back to root
        if not (out_dir_path / "index.html").exists() and (path / "index.html").exists():
            out_dir_path = path
        out_dir = str(out_dir_path)
        # For real deployments, require a token. Simulation mode will gracefully fallback.
        if mode != "simulation" and not token:
            return False, "Missing NETLIFY_AUTH_TOKEN.", None
        # Request JSON output when possible to reliably capture the deploy URL
        # Provide token via environment variable which Netlify CLI accepts reliably
        env = {"NETLIFY_AUTH_TOKEN": token} if token else None
        code, logs = run_command(["netlify", "deploy", "--prod", "--dir", out_dir, "--json"], cwd=path, token=token, timeout=600, env=env)
        # If CLI missing or timed out, try REST API fallback when token is provided
        failure_text = (logs or "").lower()
        if code != 0 and ("command not found" in failure_text or "command timed out" in failure_text or "forbidden" in failure_text or "jsonhttperror" in failure_text or "403" in failure_text):
            if token:
                # attempt direct API deploy
                try:
                    ok_api, api_logs, api_url = netlify_api_deploy(out_dir, token, project_name)
                    logs = (logs or "") + "\n" + api_logs
                    if ok_api:
                        return True, logs, api_url
                    # fall through to simulation or error
                except Exception as e:
                    logs = (logs or "") + f"\nAPI fallback failed: {e}"

            if mode == "simulation":
                logs = (logs or "") + "\nCLI unavailable or timed out; falling back to simulated deployment."
                live = fake_url(project_name, platform)
                return True, logs, live
            else:
                logs = (logs or "") + "\nCLI unavailable or timed out; install netlify-cli or use Simulation mode."
                return False, logs, None
        live = extract_url(logs)
        # If CLI reported Forbidden or JSONHTTPError, try REST API fallback
        if "forbidden" in (logs or "").lower() or "jsonhttperror" in (logs or "").lower() or "403" in (logs or ""):
            if token:
                try:
                    ok_api, api_logs, api_url = netlify_api_deploy(out_dir, token, project_name)
                    logs = (logs or "") + "\n" + api_logs
                    if ok_api:
                        return True, logs, api_url
                except Exception as e:
                    logs = (logs or "") + f"\nAPI fallback failed: {e}"

        # If extractor didn't find a URL, try to parse JSON emitted by the CLI
        json_obj = None
        if not live:
            try:
                start = logs.find('{')
                if start != -1:
                    json_obj, _ = json.JSONDecoder().raw_decode(logs[start:])
            except Exception:
                json_obj = None

        # Build list of candidate URLs (prefer site-level URL over deploy preview URL)
        candidates = []
        if json_obj and isinstance(json_obj, dict):
            # prefer top-level site URL
            for k in ("url", "deploy_ssl_url", "site_url", "deploy_url"):
                v = json_obj.get(k)
                if v and v not in candidates:
                    candidates.append(v)
            # nested deploy/site objects
            if isinstance(json_obj.get('deploy'), dict):
                for k in ('ssl_url', 'url', 'deploy_url'):
                    v = json_obj['deploy'].get(k)
                    if v and v not in candidates:
                        candidates.append(v)
            if isinstance(json_obj.get('site'), dict):
                for k in ('url', 'site_url'):
                    v = json_obj['site'].get(k)
                    if v and v not in candidates:
                        candidates.append(v)

        # If extractor found a URL earlier, ensure it's included (but keep candidates order)
        if live and live not in candidates:
            candidates.insert(0, live)

        # Try verifying each candidate in order
        verified = None
        last_reason = None
        for c in candidates:
            ok, reason = verify_live_url(c)
            if ok:
                verified = c
                break
            last_reason = reason
        if verified:
            live = verified
        # If deploy succeeded but no URL appeared in logs, try to list sites via Netlify CLI
        if code == 0 and not live:
            try:
                code2, out2 = run_command(["netlify", "sites:list", "--json", "--auth", token], cwd=path, token=token, timeout=30)
                if code2 == 0 and out2:
                    try:
                        sites = json.loads(out2)
                        match = None
                        for s in sites:
                            name = s.get('name','')
                            url = s.get('url','')
                            if project_name.lower() in (name or '').lower() or project_name.lower() in (url or '').lower():
                                match = s
                                break
                        if not match and sites:
                            match = sites[0]
                        if match:
                            live = match.get('url') or match.get('site_url') or None
                    except Exception:
                        live = None
            except Exception:
                live = None
        # If after all attempts no live URL, treat as failure for real deploys; for simulation, return fake preview
        if not live:
            if mode == "simulation":
                live = fake_url(project_name, platform)
                return True, logs + "\nNo platform URL detected; returned simulation preview.", live
            return False, logs + "\nDeployment completed but no live URL was detected.", None

        # Verify the returned live URL is reachable (avoid returning dead links)
        if mode != "simulation" and live:
            if not live.startswith(("http://", "https://")):
                live = "https://" + live
            ok, reason = verify_live_url(live)
            if not ok:
                return False, (logs or "") + f"\nDeployment reported URL {live} but verification failed: {reason}", None

        return True, logs, live

    if platform == "Vercel":
        if mode != "simulation" and not token:
            return False, "Missing VERCEL_TOKEN.", None
        code, logs = run_command(["vercel", "--prod", "--token", token, "--yes"], cwd=path, token=token, timeout=600)
        if code != 0 and ("Command not found" in (logs or "") or "Command timed out" in (logs or "")):
            if mode == "simulation":
                logs = (logs or "") + "\nCLI unavailable or timed out; falling back to simulated deployment."
                live = fake_url(project_name, platform)
                return True, logs, live
            else:
                logs = (logs or "") + "\nCLI unavailable or timed out; install vercel CLI or use Simulation mode."
                return False, logs, None
        live = extract_url(logs)
        if not live:
            if mode == "simulation":
                live = fake_url(project_name, platform)
                return True, logs + "\nNo platform URL detected; returned simulation preview.", live
            return False, logs + "\nDeployment completed but no live URL was detected.", None

        if mode != "simulation" and live:
            if not live.startswith(("http://", "https://")):
                live = "https://" + live
            ok, reason = verify_live_url(live)
            if not ok:
                return False, (logs or "") + f"\nDeployment reported URL {live} but verification failed: {reason}", None

        return True, logs, live

    if platform == "Railway":
        if mode != "simulation" and not token:
            return False, "Missing RAILWAY_TOKEN.", None

        # Support both RAILWAY_TOKEN (project token) and RAILWAY_API_TOKEN (account token)
        env = {}
        if token:
            env["RAILWAY_TOKEN"] = token
            env["RAILWAY_API_TOKEN"] = token  # some CLI versions use this var

        # Try railway CLI with --ci flag (non-interactive, exits when build completes)
        # Try several binary paths: direct 'railway', then npx @railway/cli explicitly
        railway_commands = [
            ["railway", "up", "--ci"],
        ]
        # On Windows, also try .cmd wrapper
        import sys as _sys
        if _sys.platform.startswith("win"):
            railway_commands = [
                ["railway.cmd", "up", "--ci"],
                ["railway", "up", "--ci"],
            ]
        # npx @railway/cli explicit fallback
        npx_bin = "npx.cmd" if _sys.platform.startswith("win") else "npx"
        railway_commands.append([npx_bin, "@railway/cli", "up", "--ci"])

        code, logs = 1, ""
        for railway_cmd in railway_commands:
            code, logs = run_command(railway_cmd, cwd=path, token=token, timeout=600, env=env)
            failure_text = (logs or "").lower()
            if "command not found" in failure_text:
                continue  # try next variant
            break  # used this variant (success or real failure)

        failure_text = (logs or "").lower()
        if code != 0:
            # Check if CLI truly not installed
            if "command not found" in failure_text or "command timed out" in failure_text:
                if mode == "simulation":
                    logs = (logs or "") + "\nCLI unavailable or timed out; falling back to simulated deployment."
                    live = fake_url(project_name, platform)
                    return True, logs, live
                else:
                    logs = (logs or "") + "\nCLI unavailable or timed out. Please install Railway CLI: npm install -g @railway/cli"
                    return False, logs, None
            # Handle auth failures
            if "not logged in" in failure_text or "not signed in" in failure_text or "unauthorized" in failure_text or "invalid token" in failure_text:
                return False, (logs or "") + "\nRailway authentication failed. Ensure your token is a valid Project Token (found in Railway Dashboard → Project Settings → Tokens).", None
            # Handle missing project link
            if "no project" in failure_text or "project not found" in failure_text or "not linked" in failure_text:
                return False, (logs or "") + "\nRailway project not linked. RAILWAY_TOKEN must be a Project Token (not an Account Token) to deploy without interactive setup.", None

        live = extract_url(logs)
        # Fallback: get domain using `railway domain` command
        if not live and code == 0:
            for railway_cmd_base in ([f"railway.cmd"] if _sys.platform.startswith("win") else []) + ["railway"]:
                try:
                    code_dom, logs_dom = run_command([railway_cmd_base, "domain"], cwd=path, token=token, timeout=30, env=env)
                    if code_dom == 0 and logs_dom:
                        live = extract_url(logs_dom)
                    if live:
                        break
                except Exception:
                    continue
            # Also try via npx @railway/cli
            if not live:
                try:
                    code_dom, logs_dom = run_command([npx_bin, "@railway/cli", "domain"], cwd=path, token=token, timeout=30, env=env)
                    if code_dom == 0 and logs_dom:
                        live = extract_url(logs_dom)
                except Exception:
                    pass
        if not live:
            if mode == "simulation":
                live = fake_url(project_name, platform)
                return True, logs + "\nNo platform URL detected; returned simulation preview.", live
            return False, logs + "\nDeployment completed but no live URL was detected.", None

        if mode != "simulation" and live:
            if not live.startswith(("http://", "https://")):
                live = "https://" + live
            ok, reason = verify_live_url(live)
            if not ok:
                return False, (logs or "") + f"\nDeployment reported URL {live} but verification failed: {reason}", None

        return True, logs, live

    return False, f"Real deployment for {platform} is prepared as guided mode. Use generated config file and platform dashboard/API.", None
