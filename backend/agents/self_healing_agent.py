from pathlib import Path
import json

def self_heal(root: str, detection: dict, platform_data: dict):
    path = Path(root)
    changes = []

    pkg = path / "package.json"
    if pkg.exists() and platform_data.get("build_command") == "npm run build":
        data = json.loads(pkg.read_text(encoding="utf-8"))
        scripts = data.setdefault("scripts", {})
        if "build" not in scripts:
            if "vite" in json.dumps(data).lower():
                scripts["build"] = "vite build"
            elif "react-scripts" in json.dumps(data).lower():
                scripts["build"] = "react-scripts build"
            elif "next" in json.dumps(data).lower():
                scripts["build"] = "next build"
            pkg.write_text(json.dumps(data, indent=2), encoding="utf-8")
            changes.append("Added missing build script in package.json")

    if detection["framework"] in ["Flask", "FastAPI"] and not (path / "runtime.txt").exists():
        (path / "runtime.txt").write_text("python-3.11.9\n", encoding="utf-8")
        changes.append("Added runtime.txt for Python deployment")

    return changes
