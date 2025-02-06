import logging
import os
from fastapi import FastAPI, Request, File, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from . import pdf_utils
from .config import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log the current environment and CORS settings
logger.info(f"Running in {settings.ENV} environment")
logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount the static files from the Vite build
try:
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    logger.debug("Successfully mounted /assets")
except Exception as e:
    logger.error(f"Error mounting assets: {e}")

def create_modified_filename(original_filename: str, suffix: str) -> str:
    """Create a new filename with the given suffix before the extension."""
    # Split the filename into name and extension
    name, ext = os.path.splitext(original_filename)
    return f"{name}{suffix}{ext}"

# POST endpoint to swap PDF halves
@app.post("/api/process/swap")
@limiter.limit("30/minute")
async def swap_pdf(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        processed = pdf_utils.swap_halves(contents)
        
        # Create the new filename
        new_filename = create_modified_filename(file.filename, "-swapped")
        
        # Return the processed PDF with the new filename in headers
        return Response(
            content=processed,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{new_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST endpoint to scale PDF to portrait
@app.post("/api/process/scale")
@limiter.limit("30/minute")
async def scale_pdf(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        processed = pdf_utils.scale_to_portrait(contents)
        
        # Create the new filename
        new_filename = create_modified_filename(file.filename, "-scaled")
        
        # Return the processed PDF with the new filename in headers
        return Response(
            content=processed,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{new_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static frontend files
@app.get("/{path}")
async def serve_frontend(request: Request, path: str):
    logger.debug(f"Attempting to serve path: {path}")
    
    # Special case for root path
    if path == "":
        index_path = "static/index.html"
    else:
        # Check if the path exists in static directory
        static_path = f"static/{path}"
        if os.path.exists(static_path):
            logger.debug(f"Serving static file: {static_path}")
            return FileResponse(static_path)
        index_path = "static/index.html"
    
    if os.path.exists(index_path):
        logger.debug(f"Serving index.html from {index_path}")
        return FileResponse(index_path)
    
    logger.error(f"File not found: {index_path}")
    raise HTTPException(status_code=404, detail="Not Found")

# Serve index.html for root path
@app.get("/")
async def root(request: Request):
    logger.debug("Root path requested")
    index_path = "static/index.html"
    if os.path.exists(index_path):
        logger.debug(f"Serving index.html from root path")
        return FileResponse(index_path)
    logger.error("index.html not found")
    raise HTTPException(status_code=404, detail="Not Found")