from pathlib import Path

def generate_config(project_root: str, platform_data: dict):
    root = Path(project_root)
    platform = platform_data["recommended_platform"]
    fw = platform_data["framework"]
    created = []

    if platform == "Netlify":
        publish = platform_data.get("output_folder") or "."
        command = platform_data.get("build_command") or ""
        content = f'''[build]
command = "{command}"
publish = "{publish}"

[[redirects]]
from = "/*"
to = "/index.html"
status = 200
'''
        (root / "netlify.toml").write_text(content, encoding="utf-8")
        created.append("netlify.toml")

    if platform == "Vercel" and not (root / "vercel.json").exists():
        (root / "vercel.json").write_text('{"version": 2}\n', encoding="utf-8")
        created.append("vercel.json")

    if platform in ["Railway", "Render"] and fw in ["Flask", "FastAPI", "Django"] and not (root / "Procfile").exists():
        if fw == "FastAPI":
            start = "web: uvicorn main:app --host 0.0.0.0 --port $PORT"
        elif fw == "Flask":
            start = "web: gunicorn app:app --bind 0.0.0.0:$PORT"
        else:
            start = "web: gunicorn project.wsgi --bind 0.0.0.0:$PORT"
        (root / "Procfile").write_text(start + "\n", encoding="utf-8")
        created.append("Procfile")

    if platform == "Render" and not (root / "render.yaml").exists():
        content = f'''services:
  - type: web
    name: autodeployed-service
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
'''
        (root / "render.yaml").write_text(content, encoding="utf-8")
        created.append("render.yaml")

    return created
