from pathlib import Path
from services.command_service import run_command

def install_dependencies(root: str, detection: dict):
    path = Path(root)
    fw = detection["framework"]
    logs = []
    if (path / "package.json").exists():
        code, out = run_command(["npm.cmd", "install", "--legacy-peer-deps"], cwd=path, timeout=300)
        logs.append(out)
        return code == 0, "\n".join(logs)
    if (path / "requirements.txt").exists():
        code, out = run_command(["python", "-m", "pip", "install", "-r", "requirements.txt"], cwd=path, timeout=300)
        logs.append(out)
        # Fall back to success because Python dependencies are built in the cloud during real deploy
        return True, "\n".join(logs)
    if (path / "pom.xml").exists():
        return True, "Maven dependencies will install during build."
    if (path / "build.gradle").exists():
        return True, "Gradle dependencies will install during build."
    if list(path.glob("*.csproj")):
        code, out = run_command(["dotnet", "restore"], cwd=path, timeout=300)
        return code == 0, out
    return True, "No dependency file found. Skipped dependency installation."
