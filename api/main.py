from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import tempfile
import os
import json
import uuid
from typing import Optional
import logging
from excel_tool import compare_boms

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BOM Comparison API",
    description="API for comparing Bill of Materials Excel files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Allow all origins including ngrok
    allow_credentials=False,  # Set to False when using wildcard
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "BOM Comparison API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bom-comparison-api"}

@app.options("/api/compare")
async def compare_files_options():
    """Handle preflight CORS requests"""
    return {"message": "CORS preflight handled"}

@app.post("/api/compare")
async def compare_files(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """
    Compare two BOM Excel files and return the differences.
    
    Args:
        file1: First Excel file (original)
        file2: Second Excel file (new version)
    
    Returns:
        JSON with comparison results including:
        - new_parts: Parts only in file2
        - removed_parts: Parts only in file1
        - modified_parts: Parts with different data
        - unchanged_parts: Parts with identical data
        - unrecognized_parts: Parts that couldn't be categorized
        - summary_stats: Statistics about the comparison
    """
    try:
        # Validate file types
        allowed_extensions = {'.xlsx', '.xls'}
        file1_ext = os.path.splitext(file1.filename)[1].lower()
        file2_ext = os.path.splitext(file2.filename)[1].lower()
        
        if file1_ext not in allowed_extensions or file2_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only .xlsx and .xls files are supported"
            )
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=file1_ext) as tmp1:
            content1 = await file1.read()
            tmp1.write(content1)
            tmp1_path = tmp1.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file2_ext) as tmp2:
            content2 = await file2.read()
            tmp2.write(content2)
            tmp2_path = tmp2.name
        
        try:
            # Perform comparison
            logger.info(f"Starting comparison of {file1.filename} and {file2.filename}")
            
            # Redirect stdout to suppress Unicode printing issues
            import sys
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                results = compare_boms(tmp1_path, tmp2_path)
            finally:
                sys.stdout = old_stdout
            
            logger.info("Comparison completed successfully")
            
            # Ensure JSON-serializable output (handles numpy types etc.)
            payload = jsonable_encoder(results)
            return JSONResponse(content=payload)
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(tmp1_path)
                os.unlink(tmp2_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary files: {e}")
                
    except Exception as e:
        import traceback
        logger.error(f"Error during comparison: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)