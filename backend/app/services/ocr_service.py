import easyocr
from PIL import Image

reader = easyocr.Reader(["en"], gpu=False)


def extract_text_from_image(image_path: str):

    image = Image.open(image_path)

    image = image.convert("L")

    temp_path = image_path + "_processed.png"

    image.save(temp_path)

    results = reader.readtext(temp_path, detail=0)

    text = "\n".join(results)

    return {"text": text, "confidence": None, "rotation": 0}
