from app.services.classifier_service import classify_intent


def route_question(question: str):
    result = classify_intent(question)

    intent = result["intent"]

    if intent in ["MEDICAL_ADVICE", "DIAGNOSIS_REQUEST"]:

        return {"route": "BLOCK", "intent": intent, "confidence": result["confidence"]}

    if intent in ["PATIENT_QA", "REPORT_SUMMARY", "COMPARE_REPORTS", "DOCUMENT_LIST"]:

        return {
            "route": "PATIENT_RAG",
            "intent": intent,
            "confidence": result["confidence"],
        }

    if intent == "GENERAL_HEALTH":

        return {
            "route": "GENERAL_HEALTH",
            "intent": intent,
            "confidence": result["confidence"],
        }

    return {
        "route": "OUT_OF_SCOPE",
        "intent": intent,
        "confidence": result["confidence"],
    }
