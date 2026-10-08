import os
import subprocess
import sys
token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('NETLIFY_AUTH_TOKEN')
env = os.environ.copy()
if token:
    env['NETLIFY_AUTH_TOKEN'] = token
try:
    for cmd in (['netlify','status','--json'], ['npx','netlify','status','--json']):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, env=env)
            print('CMD', ' '.join(cmd))
            print('RC', p.returncode)
            print('OUT', p.stdout)
            print('ERR', p.stderr)
        except FileNotFoundError:
            print('NOT_FOUND', cmd[0])
        except Exception as e:
            print('ERR_CMD', e)
        print('---')
except FileNotFoundError:
    print('NETLIFY_CLI_NOT_FOUND')
except Exception as e:
    print('ERR', e)
