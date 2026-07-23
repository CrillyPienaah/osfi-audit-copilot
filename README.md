# OSFI Audit Copilot — Backend

> Upload a model card, validation report, or governance policy and get an instant OSFI E-23 compliance audit — scored 0-100%, with gap analysis, risk rating, and actionable recommendations.

[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://osfi-audit-copilot-frontend.vercel.app)
[![Frontend](https://img.shields.io/badge/Frontend-GitHub-blue)](https://github.com/CrillyPienaah/osfi-audit-copilot-frontend)

---

## Live Demo

**[osfi-audit-copilot-frontend.vercel.app](https://osfi-audit-copilot-frontend.vercel.app)**

Try it with the built-in sample documents:
- Credit Scoring Model Card
- LLM Validation Report
- AI Governance Policy

---

## What It Does

OSFI Audit Copilot analyzes AI/ML model documentation against OSFI Guideline E-23 (Model Risk Management) requirements and produces a structured compliance report covering:

- Compliance score (0-100%)
- Risk rating (Low / Medium / High / Critical)
- Gap analysis across 8 E-23 categories
- Severity-ranked findings (Critical / High / Medium / Low)
- Specific actionable recommendations
- Identified strengths

---

## E-23 Compliance Categories

| Category | What It Checks |
|----------|---------------|
| Model Inventory & Risk Rating | Is the model registered and risk-classified? |
| Independent Model Validation | Was validation done before deployment? |
| Data Properties (5 required) | Accurate, relevant, compliant, traceable, timely? |
| Model Monitoring | Is ongoing drift/degradation monitoring in place? |
| Explainability & Fairness | Bias testing, adverse action reasons, SHAP? |
| Governance Structure | Board approval, three lines of defense? |
| Model Lifecycle Documentation | Design, review, deploy, monitor, decommission? |
| Scope & Regulatory Compliance | Applies to all FRFIs effective May 1 2027? |

---

## Sample Output

```json
{
  "document_name": "Credit Scoring Model Card",
  "compliance_score": 55,
  "risk_rating": "High",
  "summary": "The model demonstrates partial E-23 compliance with critical gaps in independent validation and monitoring.",
  "findings": [
    {
      "category": "Independent Model Validation",
      "status": "Non-Compliant",
      "gap": "No independent validation documented before deployment.",
      "recommendation": "Conduct independent validation including bias testing.",
      "severity": "Critical"
    }
  ],
  "critical_gaps": ["No independent validation", "No monitoring framework"],
  "strengths": ["Gradient boosting methodology documented", "AUC-ROC metric reported"]
}
```

---

## Quick Start

```bash
git clone https://github.com/CrillyPienaah/osfi-audit-copilot
cd osfi-audit-copilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uvicorn main:app --reload --port 8001
```

---

## API Reference

### POST /audit/text

```json
{
  "text": "Model card content here...",
  "document_name": "Credit Scoring Model Card v2.1"
}
```

### POST /audit/pdf

Upload a PDF file via multipart form — text is extracted and audited automatically.

### GET /samples

Returns the three built-in sample documents for demo use.

---

## Tech Stack

- **Backend:** Python, FastAPI, OpenAI GPT-4o Mini
- **Deployment:** Railway
- **Document parsing:** pypdf
- **Frontend:** Next.js on Vercel (see [osfi-audit-copilot-frontend](https://github.com/CrillyPienaah/osfi-audit-copilot-frontend))

---

## Related Projects

| Project | Description |
|---------|-------------|
| [OSFI Navigator](https://osfi-navigator-frontend.vercel.app) | RAG-powered regulatory Q&A assistant |
| [CanFinBench](https://huggingface.co/datasets/CrillyPienaah/CanFinBench) | First public LLM benchmark for Canadian financial regulatory compliance |
| [GenAI Reliability Framework](https://genai-reliability-framework.vercel.app) | LLM evaluation harness with OSFI E-23 aligned CI gates |

---

## Author

Christopher Crilly Pienaah
Portfolio: https://chris-pienaah-portfolio.vercel.app
LinkedIn: https://linkedin.com/in/christopher-crilly-pienaah
