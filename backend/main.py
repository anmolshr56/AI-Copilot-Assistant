import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.engine import ingest_pdf, get_chat_response
from backend.agent import get_agent_response
from backend.crew import run_crew_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_pdf(file_path)

    return {
        "message": f"Successfully indexed {file.filename}"
    }

@app.post("/chat")
async def chat(
    message: str = Form(...),
    use_cloud: bool = Form(False)
):
    return {
        "response": get_chat_response(message, use_cloud)
    }

@app.post("/agent-chat")
async def agent_chat(message: str = Form(...), use_cloud: bool = Form(True)):
    return {"response": get_agent_response(message, use_cloud)}

@app.post("/run-crew")
async def run_crew(topic: str = Form(...)):
    result = run_crew_task(topic)
    return {"response": str(result)}

@app.post("/shortcut")
async def shortcut(
    task: str = Form(...),
    use_cloud: bool = Form(False)
):
    prompts = {
        "summarize": "Please provide a concise summary of the document.",
        "quiz": "Generate 3 multiple choice questions based on this document.",
        "explain": "Explain the core concepts of this document as if I am 5 years old."
    }

    query = prompts.get(task, "Hello!")

    return {
        "response": get_chat_response(query, use_cloud)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)