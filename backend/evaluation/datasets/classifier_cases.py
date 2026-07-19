TEST_CASES = [
    {
        "query": "Summarize this report",
        "expected_intent": "REPORT_SUMMARY",
    },
    {
        "query": "Compare this report with my previous report",
        "expected_intent": "COMPARE_REPORTS",
    },
    {
        "query": "Explain my blood test",
        "expected_intent": "PATIENT_QA",
    },
    {
        "query": "What is diabetes?",
        "expected_intent": "GENERAL_HEALTH",
    },
    {
        "query": "Diagnose me",
        "expected_intent": "DIAGNOSIS_REQUEST",
    },
    {
        "query": "Recommend medicine",
        "expected_intent": "MEDICAL_ADVICE",
    },
    {
        "query": "Tell me a joke",
        "expected_intent": "OUT_OF_SCOPE",
    },
]