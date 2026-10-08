from pathlib import Path

IMPORTANT_FILES = [
    "package.json", "vite.config.js", "vite.config.ts", "next.config.js", "angular.json",
    "requirements.txt", "app.py", "main.py", "manage.py", "pom.xml", "build.gradle",
    "Dockerfile", "render.yaml", "netlify.toml", "vercel.json"
]

def scan_project(project_path: str):
    root = Path(project_path)
    files = []
    folders = set()
    for p in root.rglob("*"):
        if any(part in {"node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build", "target"} for part in p.parts):
            continue
        rel = p.relative_to(root).as_posix()
        if p.is_dir():
            folders.add(rel)
        else:
            files.append(rel)
    important = [f for f in files if Path(f).name in IMPORTANT_FILES or f.endswith(".csproj") or "WEB-INF/web.xml" in f]
    return {"root": str(root), "files": files[:1000], "folders": sorted(list(folders))[:300], "important_files": important}
