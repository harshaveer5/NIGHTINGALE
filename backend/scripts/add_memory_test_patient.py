import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

DATA_DIR = Path(__file__).resolve().parent / "data"
REPORTS_DIR = DATA_DIR / "reports"
PATIENTS_DIR = DATA_DIR / "patients"
PATIENTS_JSON = DATA_DIR / "patients.json"
MANIFEST_JSON = DATA_DIR / "manifest.json"


PATIENT = {
    "patient_name": "Anika Rao",
    "age": 44,
    "gender": "Female",
    "medical_history": (
        "Type 2 Diabetes for 4 years, borderline high cholesterol, mild iron "
        "deficiency anemia noted last year, and vitamin D insufficiency. No "
        "known drug allergies. No surgeries documented."
    ),
    "documents": [
        {
            "document_type": "Complete Blood Count (CBC)",
            "document_title": "Previous CBC and Iron Follow-up",
            "document_text": """Patient Name: Anika Rao

Date: 2026-01-12

Hemoglobin: 11.4 g/dL
WBC Count: 7600 cells/uL
Platelet Count: 438000 cells/uL
RBC Count: 4.08 million/uL
Mean Corpuscular Volume: 78 fL
Ferritin: 18 ng/mL

Interpretation:
Mild microcytic anemia is present. Platelet count is mildly elevated, which may be reactive in the setting of iron deficiency. White blood cell count is within range.

Doctor Note:
The clinician documented fatigue and heavier menstrual bleeding as possible contributors. Iron-rich diet and repeat CBC were discussed.""",
        },
        {
            "document_type": "Complete Blood Count (CBC)",
            "document_title": "Latest CBC and Iron Review",
            "document_text": """Patient Name: Anika Rao

Date: 2026-06-18

Hemoglobin: 12.1 g/dL
WBC Count: 7100 cells/uL
Platelet Count: 392000 cells/uL
RBC Count: 4.26 million/uL
Mean Corpuscular Volume: 82 fL
Ferritin: 29 ng/mL

Interpretation:
Hemoglobin and ferritin improved compared with the January CBC. Platelet count decreased and is now near the upper end of the reference range. No leukocytosis is seen.

Important Numbers:
Hemoglobin improved from 11.4 to 12.1 g/dL. Ferritin improved from 18 to 29 ng/mL. Platelets decreased from 438000 to 392000 cells/uL.""",
        },
        {
            "document_type": "Diabetes Monitoring Report",
            "document_title": "Latest Diabetes Control Report",
            "document_text": """Patient Name: Anika Rao

Date: 2026-06-18

Fasting Blood Glucose: 154 mg/dL
Postprandial Glucose: 218 mg/dL
HbA1c: 7.8%
Urine Microalbumin: 24 mg/g creatinine

Interpretation:
Glucose control is above the usual target range. Urine microalbumin is within the normal to mildly increased range. The clinician wrote that meal timing and medication adherence should be reviewed.

Doctor Note:
The doctor said this report is mainly about diabetes control and asked the patient to bring a home glucose log to the next appointment.""",
        },
        {
            "document_type": "Lipid Profile",
            "document_title": "Latest Lipid and Vitamin Panel",
            "document_text": """Patient Name: Anika Rao

Date: 2026-06-18

Total Cholesterol: 218 mg/dL
LDL Cholesterol: 142 mg/dL
HDL Cholesterol: 44 mg/dL
Triglycerides: 186 mg/dL
Vitamin D 25-OH: 21 ng/mL

Interpretation:
LDL cholesterol and triglycerides are elevated. Vitamin D remains insufficient. These results are relevant to cardiometabolic risk monitoring in a patient with diabetes.""",
        },
        {
            "document_type": "Prescription Record",
            "document_title": "Diabetes Lipid and Iron Medication Plan",
            "document_text": """Patient Name: Anika Rao

Date: 2026-06-18

Medication:
* Metformin extended release 1000 mg once daily with dinner
* Atorvastatin 10 mg once nightly
* Ferrous sulfate 325 mg once daily with food
* Vitamin D3 2000 IU once daily with food

Instructions:
Take iron with food if stomach upset occurs. Avoid taking iron at the same time as calcium supplements. Bring home glucose readings to the follow-up visit in 6 weeks.

Safety Note:
This record lists medications that were documented in the uploaded report. It should not be used as a new prescription or treatment recommendation.""",
        },
    ],
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def header_footer(canvas, doc, title):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(
        0.65 * inch, 0.42 * inch, "Synthetic medical test data - fictional"
    )
    canvas.drawRightString(7.85 * inch, 0.42 * inch, f"{title} | Page {doc.page}")
    canvas.restoreState()


def build_pdf(path: Path, title: str, paragraphs: list[str]):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#17313a"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTextClean",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#222222"),
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionText",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#17313a"),
            spaceBefore=5,
            spaceAfter=4,
        )
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.7 * inch,
        title=title,
    )
    story = [Paragraph(title, styles["DocTitle"])]

    for block in paragraphs:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 0.08 * inch))
            elif line.endswith(":") and not line.startswith("*"):
                story.append(Paragraph(line, styles["SectionText"]))
            elif line.startswith("* "):
                story.append(Paragraph("&bull; " + line[2:], styles["BodyTextClean"]))
            else:
                story.append(Paragraph(line, styles["BodyTextClean"]))
        story.append(Spacer(1, 0.1 * inch))

    doc.build(
        story,
        onFirstPage=lambda c, d: header_footer(c, d, title),
        onLaterPages=lambda c, d: header_footer(c, d, title),
    )


def attach_file_paths(patient: dict):
    patient_slug = slugify(patient["patient_name"])

    for index, document in enumerate(patient["documents"], start=1):
        file_name = (
            f"{patient_slug}_{index:02d}_{slugify(document['document_title'])}.pdf"
        )
        document["file_name"] = file_name
        document["file_path"] = f"backend/data/reports/{file_name}"


def main():
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    PATIENTS_DIR.mkdir(exist_ok=True)

    attach_file_paths(PATIENT)

    patients = json.loads(PATIENTS_JSON.read_text(encoding="utf-8"))
    patients = [
        patient
        for patient in patients
        if patient.get("patient_name") != PATIENT["patient_name"]
    ]
    patients.append(PATIENT)
    PATIENTS_JSON.write_text(json.dumps(patients, indent=2), encoding="utf-8")

    patient_slug = slugify(PATIENT["patient_name"])
    patient_pdf = PATIENTS_DIR / f"{patient_slug}_patient_record.pdf"
    summary_text = f"""Patient Name: {PATIENT['patient_name']}
Age: {PATIENT['age']}
Gender: {PATIENT['gender']}

Medical History:
{PATIENT['medical_history']}

Synthetic Data Notice:
This patient profile and all attached reports are entirely fictional and were generated for testing conversation memory, document selection, report comparison, and medical safety behavior."""

    patient_blocks = [summary_text]
    for document in PATIENT["documents"]:
        patient_blocks.append(
            f"{document['document_type']}: {document['document_title']}\n\n{document['document_text']}"
        )
    build_pdf(
        patient_pdf,
        f"{PATIENT['patient_name']} - Synthetic Patient Record",
        patient_blocks,
    )

    for document in PATIENT["documents"]:
        report_pdf = REPORTS_DIR / document["file_name"]
        build_pdf(report_pdf, document["document_title"], [document["document_text"]])

    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    manifest["patient_count"] = len(patients)
    manifest["document_count"] = sum(len(patient["documents"]) for patient in patients)
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
