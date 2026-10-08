import json
from pathlib import Path

def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return ""

def find_file(root: Path, name: str):
    for p in root.rglob(name):
        if "node_modules" not in p.parts and ".git" not in p.parts:
            return p
    return None

def detect_framework(project_path: str):
    root = Path(project_path)
    files = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    package_files = [p for p in root.rglob("package.json") if "node_modules" not in p.parts]
    requirements = [p for p in root.rglob("requirements.txt")]

    result = {"framework": "Unknown", "language": "Unknown", "project_type": "Unknown", "root_hint": str(root)}

    # Full stack detection
    frontend_pkg = root / "frontend" / "package.json"
    backend_pkg = root / "backend" / "package.json"
    backend_req = root / "backend" / "requirements.txt"
    if frontend_pkg.exists() and (backend_pkg.exists() or backend_req.exists()):
        ftxt = read_text(frontend_pkg)
        btxt = read_text(backend_pkg) if backend_pkg.exists() else read_text(backend_req)
        if "react" in ftxt and "fastapi" in btxt:
            return {"framework": "React + FastAPI", "language": "JavaScript + Python", "project_type": "Full Stack", "root_hint": str(root)}
        if "react" in ftxt and "flask" in btxt:
            return {"framework": "React + Flask", "language": "JavaScript + Python", "project_type": "Full Stack", "root_hint": str(root)}
        if "react" in ftxt and "express" in btxt:
            return {"framework": "MERN Stack", "language": "JavaScript", "project_type": "Full Stack", "root_hint": str(root)}
        if "angular" in ftxt and "express" in btxt:
            return {"framework": "MEAN Stack", "language": "TypeScript + JavaScript", "project_type": "Full Stack", "root_hint": str(root)}

    # Node/frontend detection
    if package_files:
        pkg = package_files[0]
        text = read_text(pkg)
        vite = find_file(root, "vite.config.js") or find_file(root, "vite.config.ts")
        if "next" in text or find_file(root, "next.config.js"):
            return {"framework": "Next.js", "language": "JavaScript/TypeScript", "project_type": "Full Stack" if "app/api" in "\n".join(files) else "Frontend", "root_hint": str(pkg.parent)}
        if "vite" in text or vite:
            fw = "React + Vite" if "react" in text else "Vue + Vite" if "vue" in text else "Vite"
            return {"framework": fw, "language": "JavaScript/TypeScript", "project_type": "Frontend", "root_hint": str(pkg.parent)}
        if "react" in text:
            return {"framework": "React", "language": "JavaScript/TypeScript", "project_type": "Frontend", "root_hint": str(pkg.parent)}
        if "angular" in text or find_file(root, "angular.json"):
            return {"framework": "Angular", "language": "TypeScript", "project_type": "Frontend", "root_hint": str(pkg.parent)}
        if "express" in text:
            return {"framework": "Express.js", "language": "JavaScript", "project_type": "Backend", "root_hint": str(pkg.parent)}

    # Python
    req_text = "\n".join(read_text(p) for p in requirements)
    app_text = "\n".join(read_text(p) for p in list(root.rglob("app.py")) + list(root.rglob("main.py")))
    if "fastapi" in req_text or "from fastapi" in app_text or "fastapi(" in app_text:
        return {"framework": "FastAPI", "language": "Python", "project_type": "Backend", "root_hint": str(requirements[0].parent if requirements else root)}
    if "flask" in req_text or "from flask" in app_text:
        return {"framework": "Flask", "language": "Python", "project_type": "Backend", "root_hint": str(requirements[0].parent if requirements else root)}
    if find_file(root, "manage.py") and any("settings.py" in f for f in files):
        return {"framework": "Django", "language": "Python", "project_type": "Backend", "root_hint": str(find_file(root, "manage.py").parent)}

    # Java
    pom = find_file(root, "pom.xml")
    gradle = find_file(root, "build.gradle")
    if pom and "spring-boot-starter" in read_text(pom):
        return {"framework": "Spring Boot", "language": "Java", "project_type": "Backend", "root_hint": str(pom.parent)}
    if gradle and "spring-boot" in read_text(gradle):
        return {"framework": "Spring Boot Gradle", "language": "Java", "project_type": "Backend", "root_hint": str(gradle.parent)}
    if any("WEB-INF/web.xml" in f for f in files):
        return {"framework": "Java Servlet", "language": "Java", "project_type": "Backend", "root_hint": str(root)}
    if pom:
        return {"framework": "Maven Java", "language": "Java", "project_type": "Backend", "root_hint": str(pom.parent)}

    # .NET
    csproj = next(root.rglob("*.csproj"), None)
    if csproj:
        return {"framework": "ASP.NET Core / .NET Web API", "language": "C#", "project_type": "Backend", "root_hint": str(csproj.parent)}

    # Static frontend
    if (root / "index.html").exists() or any(Path(f).name == "index.html" for f in files):
        return {"framework": "HTML/CSS/JS", "language": "HTML/CSS/JavaScript", "project_type": "Frontend", "root_hint": str(root)}

    return result
