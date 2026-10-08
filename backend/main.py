from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from pathlib import Path
import mimetypes
from database.database import init_db, get_deployment
from services.file_service import save_upload_zip, UPLOAD_DIR
from services.github_service import clone_repo
from agents.manager_agent import analyze as analyze_project, deploy as deploy_project

app = FastAPI(title="AutoDeploy Agent API", version="1.0.0")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_PATHS = {}

class AnalyzeRequest(BaseModel):
    project_id: str

class DeployRequest(BaseModel):
    project_id: str
    platform: str | None = None
    token: str | None = None
    mode: str = "simulation"

class GitHubRequest(BaseModel):
    repo_url: str

def get_path(project_id: str):
    path = PROJECT_PATHS.get(project_id)
    if not path:
        candidate = UPLOAD_DIR / project_id / "source"
        if candidate.exists():
            path = str(candidate)
            PROJECT_PATHS[project_id] = path
    if not path:
        raise HTTPException(status_code=404, detail="Project not found")
    return path

@app.get("/")
def root():
    return {"message": "AutoDeploy Agent API is running"}

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        project_id, path = save_upload_zip(file)
        PROJECT_PATHS[project_id] = str(path)
        return {"project_id": project_id, "message": "Uploaded and extracted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/github")
def github(req: GitHubRequest):
    try:
        project_id, path = clone_repo(req.repo_url)
        PROJECT_PATHS[project_id] = str(path)
        analysis = analyze_project(project_id, str(path))
        return {"project_id": project_id, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    path = get_path(req.project_id)
    return analyze_project(req.project_id, path)

@app.post("/deploy")
def deploy(req: DeployRequest):
    path = get_path(req.project_id)
    return deploy_project(req.project_id, path, req.platform, req.token, req.mode)

@app.get("/deployment/{project_id}")
def deployment(project_id: str):
    data = get_deployment(project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return data

@app.get("/live-url/{project_id}")
def live_url(project_id: str):
    """Returns only the live URL for a deployed project."""
    data = get_deployment(project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Deployment not found")
    url = data.get("live_url") or ""
    return {"project_id": project_id, "live_url": url, "status": data.get("status", "")}

@app.get("/preview/{project_id}", response_class=HTMLResponse)
def preview(project_id: str):
    """Return a simple placeholder page for simulation preview URLs.
    The preview URL is generated in simulation mode and does not point to a real site.
    This endpoint provides a minimal HTML response so the frontend can display something.
    """
    return f"<html><head><title>Simulation Preview</title></head><body><h2>Simulation preview for project {project_id}</h2><p>This is a simulated preview URL. No real deployment was performed.</p></body></html>"
