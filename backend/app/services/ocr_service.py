import easyocr
from PIL import Image

_reader = None


def get_reader():
    global _reader

    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)

    return _reader


def extract_text_from_image(image_path: str):

    image = Image.open(image_path)

    image = image.convert("L")

    temp_path = image_path + "_processed.png"

    image.save(temp_path)

    results = get_reader().readtext(temp_path, detail=0)

    text = "\n".join(results)

    return {"text": text, "confidence": None, "rotation": 0}
