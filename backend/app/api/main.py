import glob
import os
import shutil

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .evaluation_service import RAGEvaluator
from .rag_pipeline import RAGPipeline

app = FastAPI(title="Customer Support RAG Assistant")

rag = RAGPipeline()
evaluator = RAGEvaluator(rag)

# Folders
UPLOAD_FOLDER = "uploaded_docs"
IMAGE_FOLDER = "extracted_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Serve extracted images as static files at /images/<subfolder>/<filename>
app.mount("/images", StaticFiles(directory=IMAGE_FOLDER), name="images")


# ── Pydantic models ───────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

class SummaryResponse(BaseModel):
    summary: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "RAG API is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in (".pdf", ".pptx", ".ppt"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or PPTX file."
        )

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = rag.ingest(file_path)
        images = result.get("images", [])
        image_paths = [img["path"] for img in images]

        return {
            "message": f"'{filename}' uploaded and processed successfully.",
            "total_chunks": result.get("total_chunks", 0),
            "image_count": len(image_paths),
            "extracted_images": image_paths,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    try:
        answer = rag.ask(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/summarize", response_model=SummaryResponse)
def get_summary():
    try:
        summary = rag.summarize_document()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list-images")
def list_images():
    images = glob.glob(os.path.join(IMAGE_FOLDER, "**", "*.*"), recursive=True)
    return {"images": images, "count": len(images)}


@app.get("/evaluate")
def run_eval():
    try:
        synth_data = evaluator.generate_synthetic_qa(num_questions=3)
        if not synth_data:
            return {"results": "❌ No synthetic data generated."}
        results = evaluator.evaluate_rag(synth_data)
        formatted = "### Evaluation Results\n\n"
        for r in results:
            formatted += f"""
**Question:** {r['question']}

**RAG Answer:** {r['rag_answer']}

**Faithfulness Score:** {r['faithfulness_score']}

**Judgement:** {r['judgement']}

---
"""
        return {"results": formatted}
    except Exception as e:
        return {"results": f"❌ Eval Error: {str(e)}"}