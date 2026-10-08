import zipfile
import uuid
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Set to None for no size restriction
MAX_SIZE_MB = None

def validate_zip(file_path: Path):
    if MAX_SIZE_MB is not None:
        if file_path.stat().st_size > MAX_SIZE_MB * 1024 * 1024:
            raise ValueError(f"ZIP file too large. Maximum allowed size is {MAX_SIZE_MB} MB.")
    if not zipfile.is_zipfile(file_path):
        raise ValueError("Invalid ZIP file.")

def safe_extract(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            target = (extract_to / member).resolve()
            if not str(target).startswith(str(extract_to.resolve())):
                raise ValueError("Unsafe ZIP path detected.")
        z.extractall(extract_to)

def save_upload_zip(upload_file):
    project_id = str(uuid.uuid4())
    project_dir = UPLOAD_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    zip_path = project_dir / upload_file.filename
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    validate_zip(zip_path)
    extracted = project_dir / "source"
    extracted.mkdir(exist_ok=True)
    safe_extract(zip_path, extracted)
    return project_id, extracted

def cleanup_project(project_id: str):
    shutil.rmtree(UPLOAD_DIR / project_id, ignore_errors=True)
