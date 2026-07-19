import re
from typing import Dict

DOCUMENT_PATTERNS = {
    "CBC": [
        "hemoglobin",
        "haemoglobin",
        "wbc",
        "rbc",
        "platelet",
        "mcv",
        "mch",
        "mchc",
        "hematocrit",
        "neutrophils",
        "lymphocytes",
    ],
    "LFT": [
        "alt",
        "ast",
        "bilirubin",
        "albumin",
        "alkaline phosphatase",
        "sgpt",
        "sgot",
    ],
    "KFT": ["creatinine", "urea", "egfr", "blood urea nitrogen", "bun"],
    "LIPID_PROFILE": ["hdl", "ldl", "triglycerides", "cholesterol"],
    "THYROID": ["tsh", "t3", "t4", "thyroxine"],
    "MRI": ["mri"],
    "CT_SCAN": ["ct scan", "computed tomography"],
    "XRAY": ["x-ray", "xray"],
    "ECG": ["ecg", "ekg"],
    "PRESCRIPTION": [
        "medication",
        "medicine",
        "prescription",
        "tablet",
        "capsule",
        "take one",
        "rx",
    ],
    "DISCHARGE_SUMMARY": ["discharge summary", "hospital course", "admitted on"],
}


def detect_document_type(text: str) -> str:
    """
    Detect report type using keyword matching.
    """

    text = text.lower()

    scores = {}

    for report_type, keywords in DOCUMENT_PATTERNS.items():

        score = 0

        for keyword in keywords:

            pattern = (
                re.escape(keyword) if " " in keyword else rf"\b{re.escape(keyword)}\b"
            )

            if re.search(pattern, text):
                score += 1

        scores[report_type] = score

    best_type = max(scores, key=scores.get)

    if scores[best_type] == 0:
        return "UNKNOWN"

    return best_type


def extract_report_date(text: str):

    patterns = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group()

    return None


def extract_metadata(text: str) -> Dict:

    return {
        "document_type": detect_document_type(text),
        "report_date": extract_report_date(text),
    }
