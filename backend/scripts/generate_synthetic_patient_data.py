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


PATIENTS = [
    {
        "patient_name": "Mira Solen",
        "age": 29,
        "gender": "Female",
        "medical_history": "No major chronic conditions. Seasonal allergic rhinitis during spring. No surgeries. No known drug allergies.",
        "documents": [
            {
                "document_type": "Annual Health Checkup",
                "document_title": "Annual Wellness Visit",
                "document_text": """Patient Name: Mira Solen

Date: 2025-02-18

Reason for Visit:
Routine annual preventive health checkup.

Vitals:
Blood Pressure: 112/72 mmHg
Heart Rate: 68 bpm
Respiratory Rate: 14 breaths/min
Body Mass Index: 22.4 kg/m2

Assessment:
General examination is unremarkable. No active complaints. Sleep, appetite, and activity level are normal.

Plan:
Continue balanced diet and regular exercise. Maintain annual preventive visits and age-appropriate screening.""",
            },
            {
                "document_type": "Complete Blood Count (CBC)",
                "document_title": "CBC Report",
                "document_text": """Patient Name: Mira Solen

Date: 2025-02-18

Hemoglobin: 13.6 g/dL
WBC Count: 6900 cells/uL
Platelet Count: 274000 cells/uL
RBC Count: 4.52 million/uL
Mean Corpuscular Volume: 88 fL

Interpretation:
CBC values are within normal limits. No evidence of anemia, leukocytosis, or thrombocytopenia.""",
            },
            {
                "document_type": "Lipid Profile",
                "document_title": "Preventive Lipid Panel",
                "document_text": """Patient Name: Mira Solen

Date: 2025-02-18

Total Cholesterol: 172 mg/dL
LDL Cholesterol: 96 mg/dL
HDL Cholesterol: 58 mg/dL
Triglycerides: 91 mg/dL

Interpretation:
Lipid profile is within desirable range. Continue heart-healthy diet and physical activity.""",
            },
        ],
    },
    {
        "patient_name": "Darian Holt",
        "age": 61,
        "gender": "Male",
        "medical_history": "Hypertension for 9 years and high cholesterol for 5 years. Former smoker. Family history of coronary artery disease. No known drug allergies.",
        "documents": [
            {
                "document_type": "Blood Pressure Follow-up",
                "document_title": "Hypertension Follow-up Visit",
                "document_text": """Patient Name: Darian Holt

Date: 2025-03-06

Home Blood Pressure Log:
Average Morning Reading: 136/84 mmHg
Average Evening Reading: 132/82 mmHg
Highest Reading: 148/88 mmHg

Current Medication:
Amlodipine 5 mg once daily
Losartan 50 mg once daily

Assessment:
Blood pressure is mildly above target but improved compared with prior visit. No chest pain, shortness of breath, or ankle swelling reported.

Plan:
Continue current medications. Reduce dietary sodium. Repeat blood pressure review in 6 weeks.""",
            },
            {
                "document_type": "Lipid Profile",
                "document_title": "Cholesterol Monitoring Report",
                "document_text": """Patient Name: Darian Holt

Date: 2025-03-06

Total Cholesterol: 224 mg/dL
LDL Cholesterol: 146 mg/dL
HDL Cholesterol: 42 mg/dL
Triglycerides: 178 mg/dL

Interpretation:
LDL cholesterol and triglycerides remain elevated. Medication adherence and diet counseling reviewed.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Cardiometabolic Prescription",
                "document_text": """Patient Name: Darian Holt

Date: 2025-03-06

Medication:
* Amlodipine 5 mg once daily in the morning
* Losartan 50 mg once daily in the evening
* Atorvastatin 20 mg once nightly

Instructions:
Check blood pressure at home three times per week. Avoid missed statin doses. Follow up after 6 weeks with repeat lipid panel in 3 months.""",
            },
        ],
    },
    {
        "patient_name": "Elena Maris",
        "age": 48,
        "gender": "Female",
        "medical_history": "Type 2 Diabetes for 6 years and hypothyroidism for 3 years. History of gestational diabetes. No diabetic kidney disease documented.",
        "documents": [
            {
                "document_type": "Diabetes Monitoring Report",
                "document_title": "Quarterly Diabetes Review",
                "document_text": """Patient Name: Elena Maris

Date: 2025-04-11

Fasting Blood Glucose: 142 mg/dL
Postprandial Glucose: 196 mg/dL
HbA1c: 7.4%
Urine Microalbumin: 18 mg/g creatinine

Interpretation:
Glycemic control is above target. Kidney screening is within acceptable range. Diet consistency and medication timing discussed.""",
            },
            {
                "document_type": "Thyroid Report",
                "document_title": "Thyroid Function Test",
                "document_text": """Patient Name: Elena Maris

Date: 2025-04-11

TSH: 5.8 mIU/L
Free T4: 0.82 ng/dL
Free T3: 2.7 pg/mL

Interpretation:
TSH is mildly elevated, suggesting under-replacement of thyroid hormone. Symptoms include fatigue and dry skin.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Diabetes and Thyroid Prescription",
                "document_text": """Patient Name: Elena Maris

Date: 2025-04-11

Medication:
* Metformin extended release 1000 mg once daily with dinner
* Sitagliptin 100 mg once daily
* Levothyroxine 75 mcg once daily before breakfast

Instructions:
Take levothyroxine on an empty stomach and separate from calcium or iron supplements by 4 hours. Repeat HbA1c and TSH in 3 months.""",
            },
        ],
    },
    {
        "patient_name": "Jonah Reed",
        "age": 22,
        "gender": "Male",
        "medical_history": "Mild intermittent asthma since childhood. Uses rescue inhaler during exercise or viral illness. No hospitalizations in the past 5 years.",
        "documents": [
            {
                "document_type": "Prescription Record",
                "document_title": "Asthma Medication Renewal",
                "document_text": """Patient Name: Jonah Reed

Date: 2025-05-02

Medication:
* Albuterol inhaler 90 mcg, 2 puffs as needed for wheezing
* Fluticasone inhaler 100 mcg, 1 puff twice daily during allergy season

Instructions:
Use spacer with inhaler. Seek urgent care if rescue inhaler is needed more often than every 4 hours or symptoms do not improve.""",
            },
            {
                "document_type": "Radiology Report Summary",
                "document_title": "Chest X-ray Summary",
                "document_text": """Patient Name: Jonah Reed

Date: 2025-05-02

Study:
Chest radiograph, two views.

Findings:
Lungs are clear. No focal infiltrate, pleural effusion, or pneumothorax. Cardiomediastinal silhouette is normal in size.

Impression:
No acute cardiopulmonary abnormality.""",
            },
        ],
    },
    {
        "patient_name": "Leona Voss",
        "age": 76,
        "gender": "Female",
        "medical_history": "Elderly patient with hypertension, Type 2 Diabetes, chronic kidney disease stage 3a, and osteoarthritis. Prior uncomplicated cataract surgery.",
        "documents": [
            {
                "document_type": "Discharge Summary",
                "document_title": "Observation Stay for Dehydration",
                "document_text": """Patient Name: Leona Voss

Date: 2025-01-27

Admission Reason:
Lightheadedness and reduced oral intake after 3 days of viral gastroenteritis symptoms.

Hospital Course:
Patient received intravenous fluids and electrolyte monitoring. Blood pressure medications were temporarily held during observation. Symptoms improved and oral intake was tolerated.

Discharge Diagnoses:
* Mild dehydration, resolved
* Hypertension
* Type 2 Diabetes
* Chronic kidney disease stage 3a

Discharge Instructions:
Resume home medications except hydrochlorothiazide until primary care review. Maintain hydration and return for reduced urine output, confusion, or persistent vomiting.""",
            },
            {
                "document_type": "Kidney Function Report",
                "document_title": "Renal Panel",
                "document_text": """Patient Name: Leona Voss

Date: 2025-01-27

Serum Creatinine: 1.34 mg/dL
Blood Urea Nitrogen: 31 mg/dL
Estimated GFR: 43 mL/min/1.73m2
Sodium: 137 mmol/L
Potassium: 4.6 mmol/L

Interpretation:
Kidney function is consistent with chronic kidney disease stage 3a. Mild prerenal azotemia likely related to dehydration.""",
            },
            {
                "document_type": "Diabetes Monitoring Report",
                "document_title": "Inpatient Glucose Review",
                "document_text": """Patient Name: Leona Voss

Date: 2025-01-27

Fasting Blood Glucose: 128 mg/dL
Random Glucose Range: 118-184 mg/dL
HbA1c: 7.0%

Interpretation:
Diabetes is moderately controlled for age and comorbidity profile. No hypoglycemia recorded during observation stay.""",
            },
            {
                "document_type": "Blood Pressure Follow-up",
                "document_title": "Post-discharge Blood Pressure Plan",
                "document_text": """Patient Name: Leona Voss

Date: 2025-02-03

Clinic Blood Pressure: 124/76 mmHg
Standing Blood Pressure: 118/72 mmHg
Heart Rate: 74 bpm

Assessment:
Blood pressure is controlled after hydration improved. No recurrent dizziness.

Plan:
Continue losartan 25 mg once daily. Hold hydrochlorothiazide pending kidney function repeat in 2 weeks.""",
            },
        ],
    },
    {
        "patient_name": "Samira Kline",
        "age": 34,
        "gender": "Female",
        "medical_history": "Hypothyroidism diagnosed 2 years ago. Mild iron deficiency anemia in the past, now improved. No known drug allergies.",
        "documents": [
            {
                "document_type": "Thyroid Report",
                "document_title": "Thyroid Monitoring Report",
                "document_text": """Patient Name: Samira Kline

Date: 2025-06-14

TSH: 2.4 mIU/L
Free T4: 1.12 ng/dL
Free T3: 3.1 pg/mL

Interpretation:
Thyroid function is within target range on current levothyroxine dose.""",
            },
            {
                "document_type": "Complete Blood Count (CBC)",
                "document_title": "CBC and Anemia Follow-up",
                "document_text": """Patient Name: Samira Kline

Date: 2025-06-14

Hemoglobin: 12.2 g/dL
WBC Count: 6200 cells/uL
Platelet Count: 312000 cells/uL
Mean Corpuscular Volume: 82 fL
Ferritin: 31 ng/mL

Interpretation:
Hemoglobin is in low-normal range with improved iron stores. Continue iron-rich diet.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Thyroid Medication Renewal",
                "document_text": """Patient Name: Samira Kline

Date: 2025-06-14

Medication:
* Levothyroxine 50 mcg once daily before breakfast

Instructions:
Continue current dose. Repeat thyroid function test in 6 months or sooner if palpitations, weight change, or significant fatigue develops.""",
            },
        ],
    },
    {
        "patient_name": "Ronan Ives",
        "age": 55,
        "gender": "Male",
        "medical_history": "Type 2 Diabetes, hypertension, high cholesterol, and fatty liver noted on prior imaging. Sedentary occupation. No known drug allergies.",
        "documents": [
            {
                "document_type": "Diabetes Monitoring Report",
                "document_title": "Diabetes Control Review",
                "document_text": """Patient Name: Ronan Ives

Date: 2025-07-09

Fasting Blood Glucose: 166 mg/dL
Postprandial Glucose: 238 mg/dL
HbA1c: 8.3%
Urine Microalbumin: 42 mg/g creatinine

Interpretation:
Diabetes is uncontrolled and early albuminuria is present. Medication intensification and lifestyle plan recommended.""",
            },
            {
                "document_type": "Lipid Profile",
                "document_title": "High Cholesterol Follow-up",
                "document_text": """Patient Name: Ronan Ives

Date: 2025-07-09

Total Cholesterol: 242 mg/dL
LDL Cholesterol: 158 mg/dL
HDL Cholesterol: 38 mg/dL
Triglycerides: 246 mg/dL

Interpretation:
Atherogenic lipid pattern with elevated LDL and triglycerides. Cardiovascular risk reduction discussed.""",
            },
            {
                "document_type": "Kidney Function Report",
                "document_title": "Renal Function and Electrolytes",
                "document_text": """Patient Name: Ronan Ives

Date: 2025-07-09

Serum Creatinine: 1.02 mg/dL
Blood Urea Nitrogen: 19 mg/dL
Estimated GFR: 84 mL/min/1.73m2
Sodium: 139 mmol/L
Potassium: 4.4 mmol/L

Interpretation:
Overall kidney filtration is preserved. Albuminuria on diabetes screening requires follow-up and blood pressure optimization.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Diabetes, Blood Pressure, and Lipid Prescription",
                "document_text": """Patient Name: Ronan Ives

Date: 2025-07-09

Medication:
* Metformin extended release 1000 mg twice daily with meals
* Empagliflozin 10 mg once daily
* Telmisartan 40 mg once daily
* Rosuvastatin 20 mg once nightly

Instructions:
Monitor fasting glucose daily for 2 weeks. Maintain hydration while taking empagliflozin. Follow up in 4 weeks for tolerability review.""",
            },
        ],
    },
    {
        "patient_name": "Owen Calder",
        "age": 67,
        "gender": "Male",
        "medical_history": "Chronic obstructive sleep apnea on nightly positive airway pressure therapy, osteoarthritis, and controlled hypertension. No diabetes.",
        "documents": [
            {
                "document_type": "Blood Pressure Follow-up",
                "document_title": "Controlled Hypertension Visit",
                "document_text": """Patient Name: Owen Calder

Date: 2025-09-10

Clinic Blood Pressure: 128/78 mmHg
Home Average Blood Pressure: 126/76 mmHg
Heart Rate: 70 bpm

Assessment:
Hypertension is controlled on current therapy. Patient reports consistent use of positive airway pressure device and improved daytime alertness.

Plan:
Continue medication and home blood pressure checks twice weekly.""",
            },
            {
                "document_type": "Radiology Report Summary",
                "document_title": "Right Knee X-ray Summary",
                "document_text": """Patient Name: Owen Calder

Date: 2025-09-10

Study:
Right knee radiographs, weight-bearing views.

Findings:
Moderate medial compartment joint space narrowing with small osteophytes. No acute fracture or dislocation. No large joint effusion.

Impression:
Moderate osteoarthritic change of the right knee, greatest in the medial compartment.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Hypertension and Osteoarthritis Medication Record",
                "document_text": """Patient Name: Owen Calder

Date: 2025-09-10

Medication:
* Hydrochlorothiazide 12.5 mg once daily
* Acetaminophen 500 mg every 8 hours as needed for knee pain
* Topical diclofenac gel applied to right knee twice daily as needed

Instructions:
Avoid excessive oral anti-inflammatory medication. Continue low-impact strengthening exercises.""",
            },
        ],
    },
    {
        "patient_name": "Priya Lumen",
        "age": 19,
        "gender": "Female",
        "medical_history": "Young adult with no chronic conditions. History of mild vitamin D insufficiency. No surgeries. No known drug allergies.",
        "documents": [
            {
                "document_type": "Annual Health Checkup",
                "document_title": "College Entry Health Review",
                "document_text": """Patient Name: Priya Lumen

Date: 2025-10-03

Reason for Visit:
Pre-college health review and preventive counseling.

Vitals:
Blood Pressure: 108/68 mmHg
Heart Rate: 72 bpm
Body Mass Index: 20.8 kg/m2

Assessment:
Healthy young adult. Immunization record reviewed as complete by patient report. No exercise limitation or chronic symptoms.

Plan:
Continue balanced diet, regular physical activity, sleep hygiene, and routine preventive care.""",
            },
            {
                "document_type": "Complete Blood Count (CBC)",
                "document_title": "Baseline CBC Report",
                "document_text": """Patient Name: Priya Lumen

Date: 2025-10-03

Hemoglobin: 12.9 g/dL
WBC Count: 8100 cells/uL
Platelet Count: 286000 cells/uL
RBC Count: 4.35 million/uL
Mean Corpuscular Volume: 86 fL

Interpretation:
CBC values are within normal limits.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Vitamin Supplement Recommendation",
                "document_text": """Patient Name: Priya Lumen

Date: 2025-10-03

Medication:
* Vitamin D3 1000 IU once daily with food for 12 weeks

Instructions:
Maintain safe sunlight exposure and dietary calcium intake. Repeat vitamin D level if symptoms or risk factors develop.""",
            },
        ],
    },
    {
        "patient_name": "Nolan Vey",
        "age": 39,
        "gender": "Male",
        "medical_history": "Moderate persistent asthma and high cholesterol. Prior emergency visit for asthma flare 2 years ago. No intubation history.",
        "documents": [
            {
                "document_type": "Radiology Report Summary",
                "document_title": "Chest X-ray After Cough",
                "document_text": """Patient Name: Nolan Vey

Date: 2025-11-16

Study:
Chest radiograph, two views.

Findings:
Mild hyperinflation. No focal consolidation, pleural effusion, or pneumothorax. Cardiac silhouette is not enlarged.

Impression:
Mild hyperinflation compatible with reactive airway disease. No pneumonia.""",
            },
            {
                "document_type": "Lipid Profile",
                "document_title": "Lipid Screening Report",
                "document_text": """Patient Name: Nolan Vey

Date: 2025-11-16

Total Cholesterol: 213 mg/dL
LDL Cholesterol: 137 mg/dL
HDL Cholesterol: 45 mg/dL
Triglycerides: 154 mg/dL

Interpretation:
LDL cholesterol is above optimal range. Lifestyle therapy and repeat testing recommended.""",
            },
            {
                "document_type": "Prescription Record",
                "document_title": "Asthma Controller Prescription",
                "document_text": """Patient Name: Nolan Vey

Date: 2025-11-16

Medication:
* Budesonide-formoterol inhaler 160/4.5 mcg, 2 puffs twice daily
* Albuterol inhaler 90 mcg, 2 puffs as needed for wheezing
* Montelukast 10 mg once nightly

Instructions:
Review inhaler technique. Use controller medication daily even when symptoms are quiet. Follow up in 8 weeks.""",
            },
        ],
    },
]


def slugify(value):
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def header_footer(canvas, doc, title):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#2b4c5a"))
    canvas.drawString(
        0.65 * inch, 10.35 * inch, "Synthetic Medical AI Assistant Dataset"
    )
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(7.85 * inch, 10.35 * inch, title[:80])
    canvas.drawString(
        0.65 * inch,
        0.45 * inch,
        "Fictional training data only - not a real medical record",
    )
    canvas.drawRightString(7.85 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf(path, title, paragraphs):
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


def main():
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    PATIENTS_DIR.mkdir(exist_ok=True)

    for folder in (REPORTS_DIR, PATIENTS_DIR):
        for pdf in folder.glob("*.pdf"):
            pdf.unlink()

    for patient in PATIENTS:
        for index, document in enumerate(patient["documents"], start=1):
            document["file_name"] = (
                f"{slugify(patient['patient_name'])}_{index:02d}_{slugify(document['document_title'])}.pdf"
            )
            document["file_path"] = f"backend/data/reports/{document['file_name']}"

    (DATA_DIR / "patients.json").write_text(
        json.dumps(PATIENTS, indent=2), encoding="utf-8"
    )

    for patient in PATIENTS:
        patient_slug = slugify(patient["patient_name"])
        patient_pdf = PATIENTS_DIR / f"{patient_slug}_patient_record.pdf"
        summary_text = f"""Patient Name: {patient['patient_name']}
Age: {patient['age']}
Gender: {patient['gender']}

Medical History:
{patient['medical_history']}

Synthetic Data Notice:
This patient profile and all attached reports are entirely fictional and were generated for a Medical AI Assistant portfolio project."""

        patient_blocks = [summary_text]
        for document in patient["documents"]:
            patient_blocks.append(
                f"{document['document_type']}: {document['document_title']}\n\n{document['document_text']}"
            )
        build_pdf(
            patient_pdf,
            f"{patient['patient_name']} - Synthetic Patient Record",
            patient_blocks,
        )

        for document in patient["documents"]:
            report_pdf = REPORTS_DIR / document["file_name"]
            build_pdf(
                report_pdf, document["document_title"], [document["document_text"]]
            )

    manifest = {
        "patient_count": len(PATIENTS),
        "document_count": sum(len(patient["documents"]) for patient in PATIENTS),
        "patients_json": "backend/data/patients.json",
        "patient_pdf_directory": "backend/data/patients",
        "report_pdf_directory": "backend/data/reports",
        "notice": "All records, names, dates, results, histories, and reports are fictional synthetic data.",
    }
    (DATA_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
