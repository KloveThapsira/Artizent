import subprocess
import shlex
import os
import sys
from pathlib import Path
from typing import List, Tuple

DANGEROUS = {"rm", "del", "format", "shutdown", "reboot", "mkfs", "dd"}

def mask_token(text: str, token: str | None = None) -> str:
    if token:
        return text.replace(token, "****MASKED_TOKEN****")
    return text

def run_command(args: List[str], cwd: str | Path, token: str | None = None, timeout: int = 180, env: dict | None = None) -> Tuple[int, str]:
    if not args or args[0].lower() in DANGEROUS:
        return 1, "Blocked unsafe command."
    try:
        proc_env = None
        if env:
            proc_env = os.environ.copy()
            proc_env.update(env)
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            env=proc_env,
        )
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        return proc.returncode, mask_token(output, token)
    except FileNotFoundError:
        # Try common global locations for Node-based CLIs (helps when PATH isn't set for service users)
        cmd = args[0]
        candidates = []
        if sys.platform.startswith("win"):
            appdata = os.environ.get("APPDATA")
            if appdata:
                npm_global = os.path.join(appdata, "npm")
                candidates.extend([
                    os.path.join(npm_global, cmd + ".cmd"),
                    os.path.join(npm_global, cmd + ".ps1"),
                    os.path.join(npm_global, cmd),
                ])
        else:
            # common POSIX locations
            candidates.extend([
                os.path.join("/usr/local/bin", cmd),
                os.path.join("/usr/bin", cmd),
                os.path.join("/bin", cmd),
            ])

        for candidate in candidates:
            try:
                if candidate and os.path.exists(candidate):
                    new_args = args.copy()
                    new_args[0] = candidate
                    proc_env = None
                    if env:
                        proc_env = os.environ.copy()
                        proc_env.update(env)
                    proc = subprocess.run(
                        new_args,
                        cwd=str(cwd),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        shell=False,
                        env=proc_env,
                    )
                    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
                    return proc.returncode, mask_token(output, token)
            except Exception:
                continue

        # Try invoking via npx as a fallback for common Node CLIs (netlify, vercel, railway, etc.)
        try_npx = False
        node_clis = {"netlify", "vercel", "railway", "now", "serve"}
        if cmd and cmd.lower() in node_clis:
            try_npx = True

        if try_npx:
            npx_variants = []
            if sys.platform.startswith("win"):
                npx_variants = [["npx.cmd"] + args, ["npx"] + args]
            else:
                npx_variants = [["npx"] + args]

            for npx_args in npx_variants:
                try:
                    proc_env = None
                    if env:
                        proc_env = os.environ.copy()
                        proc_env.update(env)
                    proc = subprocess.run(
                        npx_args,
                        cwd=str(cwd),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        shell=False,
                        env=proc_env,
                    )
                    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
                    return proc.returncode, mask_token(output, token)
                except FileNotFoundError:
                    continue
                except Exception:
                    continue

        return 1, f"Command not found: {args[0]}. Install it or ensure it's on PATH, or use simulation mode."
    except subprocess.TimeoutExpired:
        return 1, "Command timed out."
