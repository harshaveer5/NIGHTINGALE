import fitz


def extract_text_from_pdf(pdf_path: str):

    documnet = fitz.open(pdf_path)

    text = ""

    for page in documnet:
        text += page.get_text()

    documnet.close()

    return text
