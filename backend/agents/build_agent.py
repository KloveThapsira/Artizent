from pathlib import Path
from services.command_service import run_command

def build_project(root: str, platform_data: dict):
    path = Path(root)
    fw = platform_data["framework"]
    cmd = platform_data.get("build_command", "")
    if cmd in ["", "No frontend build required", "Build frontend and backend separately"]:
        return True, f"Build skipped: {cmd or 'static project'}"
    if cmd == "npm run build":
        code, out = run_command(["npm.cmd", "run", "build"], cwd=path, timeout=300)
        return code == 0, out
    if "mvn" in cmd:
        code, out = run_command(["mvn", "clean", "package"], cwd=path, timeout=500)
        return code == 0, out
    if "gradle" in cmd:
        code, out = run_command(["gradle", "build"], cwd=path, timeout=500)
        return code == 0, out
    if "dotnet" in cmd:
        code, out = run_command(["dotnet", "publish", "-c", "Release"], cwd=path, timeout=500)
        return code == 0, out
    return True, "Unknown build command. Skipped for safety."
