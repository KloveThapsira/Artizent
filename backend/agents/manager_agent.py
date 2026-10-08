from pathlib import Path
from agents.analyzer_agent import scan_project
from agents.framework_agent import detect_framework
from agents.platform_agent import select_platform
from agents.config_agent import generate_config
from agents.self_healing_agent import self_heal
from agents.dependency_agent import install_dependencies
from agents.build_agent import build_project
from agents.deploy_agent import deploy_project
from agents.error_agent import explain_error
from database.database import upsert_deployment, get_deployment
from services.token_service import required_token_for, validate_token

def analyze(project_id: str, project_path: str):
    scan = scan_project(project_path)
    detection = detect_framework(project_path)
    platform_data = select_platform(detection)
    root = detection.get("root_hint") or project_path
    configs = generate_config(root, platform_data)
    fixes = self_heal(root, detection, platform_data)

    data = {
        "project_id": project_id,
        "project_name": Path(root).name,
        "framework": platform_data["framework"],
        "language": platform_data["language"],
        "project_type": platform_data["project_type"],
        "platform": platform_data["recommended_platform"],
        "build_command": platform_data["build_command"],
        "output_folder": platform_data["output_folder"],
        "status": "Framework Detected",
        "live_url": "",
        "logs": f"Analysis complete. Configs: {configs}. Self-healing: {fixes}",
    }
    upsert_deployment(data)
    return {"scan": scan, "detection": detection, "deployment_plan": platform_data, "configs_created": configs, "self_healing": fixes}

def deploy(project_id: str, project_path: str, platform: str | None, token: str | None, mode: str = "simulation"):
    detection = detect_framework(project_path)
    platform_data = select_platform(detection)
    if platform:
        platform_data["recommended_platform"] = platform
        platform_data["token_name"] = required_token_for(platform)
        # Validate the provided token against the expected environment variable
        validate_token(platform, token)

    root = detection.get("root_hint") or project_path
    logs = []

    ok, out = install_dependencies(root, detection)
    logs.append("=== Dependency Agent ===\n" + out)
    if not ok:
        err = explain_error(out)
        upsert_deployment({"project_id": project_id, "project_name": Path(root).name, "framework": detection["framework"], "language": detection["language"], "project_type": detection["project_type"], "platform": platform_data["recommended_platform"], "build_command": platform_data["build_command"], "output_folder": platform_data["output_folder"], "status": "Failed", "live_url": "", "logs": "\n".join(logs) + "\n" + err})
        return {"status": "Failed", "live_url": None, "logs": "\n".join(logs), "error_explanation": err}

    ok, out = build_project(root, platform_data)
    logs.append("=== Build Agent ===\n" + out)
    if not ok:
        fixes = self_heal(root, detection, platform_data)
        logs.append("=== Self-Healing Agent ===\n" + str(fixes))
        err = explain_error(out)
        upsert_deployment({"project_id": project_id, "project_name": Path(root).name, "framework": detection["framework"], "language": detection["language"], "project_type": detection["project_type"], "platform": platform_data["recommended_platform"], "build_command": platform_data["build_command"], "output_folder": platform_data["output_folder"], "status": "Failed", "live_url": "", "logs": "\n".join(logs) + "\n" + err})
        return {"status": "Failed", "live_url": None, "logs": "\n".join(logs), "error_explanation": err}

    ok, out, live = deploy_project(root, platform_data, token=token, mode=mode, project_id=project_id)
    logs.append("=== Deployment Agent ===\n" + out)
    status = "Success" if ok else "Failed"
    err = "" if ok else explain_error(out)
    upsert_deployment({"project_id": project_id, "project_name": Path(root).name, "framework": detection["framework"], "language": detection["language"], "project_type": detection["project_type"], "platform": platform_data["recommended_platform"], "build_command": platform_data["build_command"], "output_folder": platform_data["output_folder"], "status": status, "live_url": live or "", "logs": "\n".join(logs) + ("\n" + err if err else "")})
    return {"status": status, "live_url": live, "logs": "\n".join(logs), "error_explanation": err}
