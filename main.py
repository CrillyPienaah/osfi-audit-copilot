from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from audit import run_audit

load_dotenv()

app = FastAPI(title="OSFI Audit Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextAuditRequest(BaseModel):
    text: str
    document_name: Optional[str] = "Uploaded Document"

class AuditFinding(BaseModel):
    category: str
    requirement: str
    status: str
    gap: Optional[str]
    recommendation: Optional[str] = ""
    regulatory_source: str
    severity: str

class AuditResponse(BaseModel):
    document_name: str
    compliance_score: int
    risk_rating: str
    summary: str
    findings: list[AuditFinding]
    critical_gaps: list[str]
    strengths: list[str]

@app.get("/")
def root():
    return {"status": "OSFI Audit Copilot API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/audit/text", response_model=AuditResponse)
async def audit_text(request: TextAuditRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty")
    try:
        result = await run_audit(text=request.text, document_name=request.document_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/audit/pdf", response_model=AuditResponse)
async def audit_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    try:
        import tempfile, pypdf
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        reader = pypdf.PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        os.unlink(tmp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        result = await run_audit(text=text, document_name=file.filename)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/samples")
def get_samples():
    return {"samples": [
        {"id": "model_card", "name": "Credit Scoring Model Card", "description": "AI model card for a credit risk scoring system"},
        {"id": "validation_report", "name": "LLM Validation Report", "description": "Model validation report for a generative AI system"},
        {"id": "governance_policy", "name": "AI Governance Policy", "description": "Enterprise AI governance and risk management policy"},
    ]}

