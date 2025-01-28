from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
import os
from pathlib import Path

from ..utils.text_processor import TextProcessor
from ..utils.ai_handler import AIHandler

app = FastAPI(title="Script Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our utilities
text_processor = TextProcessor()
ai_handler = AIHandler()

# Store background tasks
active_tasks = {}

class ScriptRequest(BaseModel):
    content: str
    highlighted_concept: Optional[str] = None
    previous_topic: Optional[str] = None

class ScriptResponse(BaseModel):
    task_id: str
    status: str
    script: Optional[str] = None
    validation: Optional[Dict] = None
    error: Optional[str] = None

@app.post("/api/generate-script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest, background_tasks: BackgroundTasks):
    """Generate a script from the provided content."""
    task_id = str(len(active_tasks))
    
    async def process_script():
        try:
            # Process the text in chunks
            chunks = text_processor.chunk_text(request.content)
            
            # Process chunks in parallel
            processed_chunks = await text_processor.process_chunks(chunks)
            
            # Generate the full script
            script = await ai_handler.generate_script(
                content=request.content,
                highlighted_concept=request.highlighted_concept,
                previous_topic=request.previous_topic
            )
            
            # Validate the script
            validation_results = text_processor.validate_script(script)
            
            # If validation fails, try to improve the script
            if not all(v["pass"] for v in validation_results.values()):
                script = await ai_handler.improve_script(script, validation_results)
                validation_results = text_processor.validate_script(script)
            
            active_tasks[task_id] = {
                "status": "completed",
                "script": script,
                "validation": validation_results
            }
            
        except Exception as e:
            active_tasks[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Start the background task
    active_tasks[task_id] = {"status": "processing"}
    background_tasks.add_task(process_script)
    
    return ScriptResponse(
        task_id=task_id,
        status="processing"
    )

@app.get("/api/script-status/{task_id}", response_model=ScriptResponse)
async def get_script_status(task_id: str):
    """Get the status of a script generation task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    return ScriptResponse(
        task_id=task_id,
        status=task["status"],
        script=task.get("script"),
        validation=task.get("validation"),
        error=task.get("error")
    )

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and extract its content."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        return JSONResponse({
            "status": "success",
            "content": text_content
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing file: {str(e)}"
        )

@app.post("/api/validate-script")
async def validate_script(script: str):
    """Validate a script against quality criteria."""
    try:
        validation_results = text_processor.validate_script(script)
        return JSONResponse({
            "status": "success",
            "validation": validation_results
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error validating script: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
