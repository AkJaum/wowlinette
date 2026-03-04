from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
import uuid
from app.unzip import unzip_file
from app.runner import run_all_tests, get_available_lists

app = FastAPI()

# Configurar CORS para localhost e domínios da Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://my-own-moulinette.vercel.app"
        ,"https://wowlinette.vercel.app/",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Wowlinette API is running"}

@app.get("/lists")
async def get_lists():
    """Return available lists for evaluation"""
    available_lists = get_available_lists()
    return {"lists": available_lists}

@app.post("/wowlinette")
async def wowlinette(file: UploadFile = File(...), list_name: str = Form("list_00")):
    """
    Evaluate a submitted file against a specific list.
    
    Args:
        file: The ZIP file to evaluate
        list_name: The list to test against (e.g., "list_00", "list_01")
    """
    # Create a unique temporary directory for this request
    request_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), f"wowlinette_{request_id}")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        print(f"[{request_id}] Created temp dir: {temp_dir}")
        print(f"[{request_id}] Testing list: {list_name}")
        
        # Save uploaded file in the request's temp directory
        zip_path = os.path.join(temp_dir, file.filename)

        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[{request_id}] Saved ZIP to: {zip_path}")

        # Extract to the request's temp directory
        unzip_file(zip_path, temp_dir)

        print(f"[{request_id}] Extracted files")

        # Run tests with the request's temp directory and specified list
        results = run_all_tests(temp_dir, list_name)

        print(f"[{request_id}] Test results: {results}")
        return results

    except Exception as e:
        print(f"[{request_id}] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    finally:
        # Clean up the request's temp directory
        print(f"[{request_id}] Cleaning up temp directory")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
