import uuid
from pathlib import Path
from .command_service import run_command
from .file_service import UPLOAD_DIR

def clone_repo(repo_url: str):
    if not repo_url.startswith(("https://github.com/", "git@github.com:")):
        raise ValueError("Only GitHub repository URLs are allowed.")
    project_id = str(uuid.uuid4())
    target = UPLOAD_DIR / project_id / "source"
    target.parent.mkdir(parents=True, exist_ok=True)
    code, logs = run_command(["git", "clone", "--depth", "1", repo_url, str(target)], cwd=UPLOAD_DIR)
    if code != 0:
        raise RuntimeError(logs)
    return project_id, target
