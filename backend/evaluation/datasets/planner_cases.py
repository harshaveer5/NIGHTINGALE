TEST_CASES = [
    {
        "query": "Summarize this report",
        "expected_plan": "REPORT_SUMMARY",
    },
    {
        "query": "Compare my reports",
        "expected_plan": "COMPARE_DOCUMENTS",
    },
    {
        "query": "Explain hemoglobin",
        "expected_plan": "PATIENT_QA",
    },
    {
        "query": "What is diabetes?",
        "expected_plan": "GENERAL_HEALTH",
    },
]