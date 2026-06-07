import os
import asyncio
import json
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

E23_CORPUS = [
    Document(page_content="OSFI E-23 requires FRFIs to maintain a comprehensive model inventory covering all models including AI/ML systems. The inventory must document model purpose, risk rating, validation status, and lifecycle stage. Models must be classified by inherent and residual risk using quantitative factors (portfolio size, financial impact) and qualitative factors (autonomy level, complexity, customer impact, regulatory risk).", metadata={"source": "OSFI E-23", "section": "Model Inventory & Risk Rating"}),
    Document(page_content="OSFI E-23 mandates independent model validation before initial deployment and for all material changes. Validation must assess conceptual soundness, data quality, and performance on representative samples. For AI/ML models, validation must include bias testing, fairness assessment, and explainability evaluation. Third-party models require the same validation standards - FRFIs cannot outsource model risk accountability.", metadata={"source": "OSFI E-23", "section": "Independent Model Validation"}),
    Document(page_content="OSFI E-23 requires five data properties for all model data: (1) Accurate and fit-for-use, (2) Relevant and representative of the deployment population, (3) Compliant with applicable laws and regulations, (4) Traceable with documented lineage and provenance, (5) Timely and refreshed at appropriate frequencies. Data bias must be identified and managed, especially for AI/ML models.", metadata={"source": "OSFI E-23", "section": "Data Properties"}),
    Document(page_content="OSFI E-23 requires ongoing model monitoring after deployment to detect drift, degradation, and anomalies. Monitoring must track accuracy metrics, data drift, and model behavior. For AI/ML models with autonomous decision-making, monitoring must detect autonomous re-parametrization. Performance thresholds must be validated as appropriate for the use case. Findings must trigger escalation per the model risk governance framework.", metadata={"source": "OSFI E-23", "section": "Model Monitoring"}),
    Document(page_content="OSFI E-23 requires AI/ML models to have appropriate explainability and transparency. Black-box approaches require alternative controls. Credit decision models must provide adverse action reasons. Bias and fairness testing is required - models that produce discriminatory outcomes must be suspended until remediated. The Canadian Human Rights Act prohibits discriminatory lending decisions.", metadata={"source": "OSFI E-23", "section": "Explainability & Fairness"}),
    Document(page_content="OSFI E-23 governance requires Board approval of the model risk management framework and risk appetite. Senior Management implements the framework. Three lines of defense: model developers (1st line), model risk management (2nd line), internal audit (3rd line). High-risk models require higher approval authority, more frequent review cycles, and more detailed documentation. Model changes require change management and approval before deployment.", metadata={"source": "OSFI E-23", "section": "Governance Structure"}),
    Document(page_content="OSFI E-23 model lifecycle covers five stages: (1) Model Design - rationale, data, development methodology, (2) Model Review - independent validation before deployment, (3) Model Deployment - change management and approval, (4) Model Monitoring - ongoing performance surveillance, (5) Model Decommission - documented retirement with dependency assessment. Each stage has specific documentation and governance requirements.", metadata={"source": "OSFI E-23", "section": "Model Lifecycle"}),
    Document(page_content="OSFI E-23 applies to all Federally Regulated Financial Institutions (FRFIs) effective May 1 2027. Scope includes banks, foreign bank branches, life insurers, P&C insurers, and trust and loan companies. Covers all models including AI/ML systems, generative AI, agentic systems, and IT services. The OECD definition of AI system is adopted. Risk-based and proportional approach - governance intensity scales with model risk rating.", metadata={"source": "OSFI E-23", "section": "Scope & Application"}),
]

AUDIT_PROMPT = """You are an expert OSFI E-23 compliance auditor analyzing a document submitted by a Canadian federally regulated financial institution (FRFI).

Analyze the document against OSFI Guideline E-23 (Model Risk Management) requirements and produce a structured compliance audit report.

E-23 REFERENCE CORPUS:
{context}

DOCUMENT TO AUDIT:
{document}

Produce a JSON compliance audit report with this EXACT structure:
{{
  "compliance_score": <integer 0-100>,
  "risk_rating": <"Low" | "Medium" | "High" | "Critical">,
  "summary": "<2-3 sentence executive summary of compliance status>",
  "findings": [
    {{
      "category": "<E-23 requirement category>",
      "requirement": "<specific E-23 requirement>",
      "status": <"Compliant" | "Partial" | "Non-Compliant" | "Not Assessed">,
      "gap": "<specific gap identified or null if compliant>",
      "recommendation": "<specific actionable recommendation>",
      "regulatory_source": "OSFI Guideline E-23",
      "severity": <"Critical" | "High" | "Medium" | "Low">
    }}
  ],
  "critical_gaps": ["<list of critical missing items>"],
  "strengths": ["<list of what the document does well>"]
}}

Evaluate against these E-23 categories:
1. Model Inventory & Risk Rating
2. Independent Model Validation
3. Data Properties (5 required)
4. Model Monitoring
5. Explainability & Fairness
6. Governance Structure
7. Model Lifecycle Documentation
8. Scope & Regulatory Compliance

Return ONLY valid JSON. No preamble, no markdown, no explanation."""

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_documents(E23_CORPUS)
        _vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    return _vectorstore

def get_risk_rating(score: int) -> str:
    if score >= 80: return "Low"
    if score >= 60: return "Medium"
    if score >= 40: return "High"
    return "Critical"

async def run_audit(text: str, document_name: str = "Document") -> dict:
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(None, retriever.invoke, text[:500])
    context = "\n\n".join([f"[{d.metadata.get('source')} - {d.metadata.get('section')}]\n{d.page_content}" for d in docs])
    doc_excerpt = text[:4000] if len(text) > 4000 else text
    prompt = ChatPromptTemplate.from_messages([("human", AUDIT_PROMPT)])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    chain = prompt | llm
    response = await loop.run_in_executor(None, lambda: chain.invoke({"context": context, "document": doc_excerpt}))
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    if "risk_rating" not in result:
        result["risk_rating"] = get_risk_rating(result.get("compliance_score", 0))
    result["document_name"] = document_name
    if "critical_gaps" not in result:
        result["critical_gaps"] = []
    if "strengths" not in result:
        result["strengths"] = []
    return result
