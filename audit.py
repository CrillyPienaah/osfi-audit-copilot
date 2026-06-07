import os
import asyncio
import json
from langchain_openai import ChatOpenAI

E23_CORPUS = [
    {"source": "OSFI E-23", "section": "Model Inventory & Risk Rating", "content": "OSFI E-23 requires FRFIs to maintain a comprehensive model inventory covering all models including AI/ML systems. The inventory must document model purpose, risk rating, validation status, and lifecycle stage. Models must be classified by inherent and residual risk using quantitative and qualitative factors including autonomy level, complexity, customer impact, and regulatory risk."},
    {"source": "OSFI E-23", "section": "Independent Model Validation", "content": "OSFI E-23 mandates independent model validation before initial deployment and for all material changes. Validation must assess conceptual soundness, data quality, and performance. For AI/ML models, validation must include bias testing, fairness assessment, and explainability evaluation. Third-party models require the same validation standards."},
    {"source": "OSFI E-23", "section": "Data Properties", "content": "OSFI E-23 requires five data properties: (1) Accurate and fit-for-use, (2) Relevant and representative, (3) Compliant with applicable laws, (4) Traceable with documented lineage, (5) Timely and refreshed appropriately. Data bias must be identified and managed."},
    {"source": "OSFI E-23", "section": "Model Monitoring", "content": "OSFI E-23 requires ongoing model monitoring after deployment to detect drift, degradation, and anomalies. Monitoring must track accuracy metrics and data drift. For autonomous AI/ML models, monitoring must detect autonomous re-parametrization. Performance thresholds must trigger escalation per the model risk governance framework."},
    {"source": "OSFI E-23", "section": "Explainability & Fairness", "content": "OSFI E-23 requires AI/ML models to have appropriate explainability and transparency. Black-box approaches require alternative controls. Credit decision models must provide adverse action reasons. Bias and fairness testing is required."},
    {"source": "OSFI E-23", "section": "Governance Structure", "content": "OSFI E-23 governance requires Board approval of the model risk management framework. Three lines of defense: model developers first line, model risk management second line, internal audit third line. High-risk models require higher approval authority and more frequent review cycles."},
    {"source": "OSFI E-23", "section": "Model Lifecycle", "content": "OSFI E-23 model lifecycle covers five stages: Model Design, Model Review with independent validation, Model Deployment with change management, Model Monitoring with ongoing surveillance, and Model Decommission with documented retirement."},
    {"source": "OSFI E-23", "section": "Scope & Application", "content": "OSFI E-23 applies to all Federally Regulated Financial Institutions effective May 1 2027. Covers banks, foreign bank branches, life insurers, P&C insurers, and trust companies. Covers all models including AI/ML systems, generative AI, and agentic systems."},
]

CONTEXT = "\n\n".join(
    f"[{item['source']} - {item['section']}]\n{item['content']}"
    for item in E23_CORPUS
)

AUDIT_PROMPT = """You are an expert OSFI E-23 compliance auditor.

Analyze the document against OSFI Guideline E-23 Model Risk Management requirements.

E-23 REFERENCE:
{context}

DOCUMENT:
{document}

Return ONLY valid JSON with no markdown, no backticks, no preamble. Start your response with {{ and end with }}. Use this structure:
{{"compliance_score": <integer 0-100>, "risk_rating": "<Low|Medium|High|Critical>", "summary": "<2-3 sentences>", "findings": [{{"category": "<string>", "requirement": "<string>", "status": "<Compliant|Partial|Non-Compliant|Not Assessed>", "gap": "<string or null>", "recommendation": "<string>", "regulatory_source": "OSFI Guideline E-23", "severity": "<Critical|High|Medium|Low>"}}], "critical_gaps": ["<string>"], "strengths": ["<string>"]}}"""


async def run_audit(text: str, document_name: str = "Document") -> dict:
    doc_excerpt = text[:4000] if len(text) > 4000 else text
    prompt = AUDIT_PROMPT.format(context=CONTEXT, document=doc_excerpt)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: llm.invoke(prompt))

    raw = response.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    result = json.loads(raw)
    result["document_name"] = document_name
    if "critical_gaps" not in result:
        result["critical_gaps"] = []
    if "strengths" not in result:
        result["strengths"] = []
    return result
