import numpy as np
from app.core.logging import logger
from sentence_transformers import SentenceTransformer

# ==========================================================
# Model
# ==========================================================

_model = None


def get_model():
    global _model

    if _model is None:
        logger.info("Loading classifier model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Classifier model loaded.")

    return _model

# ==========================================================
# Configuration
# ==========================================================

HIGH_CONFIDENCE = 0.85
MEDIUM_CONFIDENCE = 0.70
MIN_CONFIDENCE = 0.55

DEBUG_CLASSIFIER = False

# ==========================================================
# Intent Examples
# ==========================================================

INTENTS = {
    "PATIENT_QA": [
        # --------------------------
        # Patient Details
        # --------------------------
        "What is the patient's age?",
        "How old is the patient?",
        "What is the patient's gender?",
        "Show patient details.",
        "Show patient information.",
        "Summarize this patient's history.",
        "What medical history does the patient have?",
        "Does the patient have allergies?",
        "What medications is this patient taking?",
        "What should I be worried about?",
        "Can you explain this like I'm five?",
        "What did the doctor say?",
        "Why did they order this test?",
        "What are the important numbers?",
        "Show me the abnormal values.",
        "Which medicine is mentioned?",
        "I forgot what this report was about.",
        "What should I ask my doctor?",
        # --------------------------
        # CBC
        # --------------------------
        "What is the hemoglobin level?",
        "Show hemoglobin.",
        "What is the WBC count?",
        "Show platelet count.",
        "Explain platelet count.",
        "What is the RBC count?",
        "Explain CBC report.",
        "What does the blood report show?",
        "Are there any abnormal blood values?",
        "Show me my latest blood report.",
        "Which reports are related to diabetes?",
        # --------------------------
        # Biochemistry
        # --------------------------
        "What is the glucose level?",
        "Explain blood sugar.",
        "What is the creatinine level?",
        "Show kidney function.",
        "Explain liver function.",
        "What is the cholesterol value?",
        "Show lipid profile.",
        "Explain ferritin.",
        "What is the vitamin D level?",
        # --------------------------
        # Radiology
        # --------------------------
        "Explain MRI findings.",
        "Explain CT scan.",
        "Explain X-ray report.",
        "Explain ultrasound report.",
        "Explain ECG report.",
        "Explain this scan.",
        "What abnormalities are present?",
        "Explain imaging findings.",
        # --------------------------
        # Prescriptions
        # --------------------------
        "What medicines are prescribed?",
        "Show medications.",
        "Explain the prescription.",
        "What dosage is mentioned?",
        "How often should the medicine be taken?",
        # --------------------------
        # Follow-ups
        # --------------------------
        "Explain that.",
        "Explain further.",
        "What does that mean?",
        "Can you explain more?",
        "Tell me more.",
        "What about the platelet count?",
        "What about glucose?",
        "Compare with previous report.",
        "Is that normal?",
        "Is it improving?",
        "Is anything getting worse?",
        "Has anything improved?",
        "What changed since last time?",
        "Did anything change from my previous visit?",
        "Continue.",
        "Go on.",
    ],
    "REPORT_SUMMARY": [
        "Summarize this report.",
        "Summarize this document.",
        "Summarize the blood report.",
        "Summarize the MRI report.",
        "Summarize lab results.",
        "Give me a report summary.",
        "Explain the overall findings.",
        "What does this report say?",
        "What happened in my latest report?",
        "What is this paper about?",
        "Summarize everything.",
        "Tell me my medical story.",
        "Provide key findings.",
        "Give me an overview.",
        "Provide a short summary.",
    ],
    "COMPARE_REPORTS": [
        "Compare my reports.",
        "Compare this report with the previous report.",
        "What changed since last time?",
        "Did anything change from my previous visit?",
        "Is anything getting worse?",
        "Has anything improved?",
        "What improved between reports?",
        "What got worse compared to before?",
    ],
    "DOCUMENT_LIST": [
        "What reports do I have?",
        "Show me my reports.",
        "List my uploaded documents.",
        "Which reports are related to diabetes?",
        "Show me my latest blood report.",
        "What documents are available?",
    ],
    "GENERAL_HEALTH": [
        "What is diabetes?",
        "Explain hypertension.",
        "What causes asthma?",
        "What is cholesterol?",
        "Explain anemia.",
        "What causes fever?",
        "Explain insulin.",
        "Explain blood pressure.",
        "What is vitamin D deficiency?",
        "What is thyroid disease?",
    ],
    "MEDICAL_ADVICE": [
        "What medicine should I take?",
        "Recommend treatment.",
        "What drug should I use?",
        "How should I treat this?",
        "Can I take antibiotics?",
        "Should I start taking metformin?",
        "Recommend medication.",
    ],
    "DIAGNOSIS_REQUEST": [
        "Diagnose me.",
        "Do I have cancer?",
        "What disease do I have?",
        "Can you diagnose this report?",
        "What illness is this?",
        "Tell me my diagnosis.",
    ],
    "OUT_OF_SCOPE": [
        "Who won the IPL?",
        "Write Python code.",
        "Tell me a joke.",
        "What is the capital of France?",
        "Write an essay.",
        "Translate this sentence.",
    ],
}

# ==========================================================
# Build Example Embeddings
# ==========================================================


def _build_example_embeddings():
    """
    Build a searchable embedding index.
    This runs ONLY once when the server starts.
    """

    examples = []
    embeddings = []

    for intent, phrases in INTENTS.items():

        vectors = get_model().encode(
            phrases, convert_to_numpy=True, normalize_embeddings=True
        )

        for text, vector in zip(phrases, vectors):

            examples.append({"intent": intent, "text": text})

            embeddings.append(vector)

    return examples, np.vstack(embeddings)


# Build once at startup
EXAMPLES = None
EMBEDDING_MATRIX = None

def get_classifier_index():
    global EXAMPLES, EMBEDDING_MATRIX

    if EXAMPLES is None or EMBEDDING_MATRIX is None:
        logger.info("Building classifier embedding index...")
        EXAMPLES, EMBEDDING_MATRIX = _build_example_embeddings()
        logger.info("Classifier embedding index ready.")

    return EXAMPLES, EMBEDDING_MATRIX


# ==========================================================
# Similarity Search
# ==========================================================


def _find_best_matches(query_embedding: np.ndarray, top_k: int = 3):
    """
    Fast semantic search using matrix multiplication.
    Since all embeddings are normalized,
    cosine similarity == dot product.
    """

    examples, matrix = get_classifier_index()

    scores = matrix @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    matches = []

    for idx in top_indices:

        matches.append(
            {
                "intent": examples[idx]["intent"],
                "example": examples[idx]["text"],
                "score": float(scores[idx]),
            }
        )

    return matches


# ==========================================================
# Intent Classification
# ==========================================================


def classify_intent(question: str) -> dict:
    """
    Classify a user question into one of the supported intents.
    """

    query_embedding = get_model().encode(
        question, convert_to_numpy=True, normalize_embeddings=True
    )

    matches = _find_best_matches(query_embedding, top_k=3)

    best_match = matches[0]

    if DEBUG_CLASSIFIER:
        logger.info("Intent classifier question=%s", question)

        for i, match in enumerate(matches, start=1):
            logger.info(
                "Intent match %s | intent=%s | score=%.3f | example=%s",
                i,
                match["intent"],
                match["score"],
                match["example"],
            )

    if best_match["score"] < MIN_CONFIDENCE:

        return {
            "intent": "OUT_OF_SCOPE",
            "confidence": float(best_match["score"]),
            "matched_example": best_match["example"],
            "top_matches": matches,
        }

    return {
        "intent": best_match["intent"],
        "confidence": float(best_match["score"]),
        "matched_example": best_match["example"],
        "top_matches": matches,
    }
