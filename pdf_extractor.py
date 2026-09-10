import pdfplumber
import re


def _is_garbled(text):
    """Check if extracted text is garbled (single chars per line = scanned PDF)."""
    if not text:
        return True
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return True
    # If majority of lines are single characters, it's garbled
    single_char_lines = sum(1 for l in lines if len(l) == 1)
    return (single_char_lines / len(lines)) > 0.5


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF.
    Tries pdfplumber first; falls back to OCR (pytesseract) for scanned/image PDFs.
    """
    # Try pdfplumber first
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass

    # If text is empty or garbled, use OCR
    if _is_garbled(text):
        text = _ocr_extract(file_path)

    return text.strip()


def _ocr_extract(file_path):
    """Use pytesseract OCR to extract text from scanned PDF pages."""
    try:
        from pdf2image import convert_from_path
        import pytesseract

        pages = convert_from_path(file_path, dpi=200)
        all_text = ""
        for page in pages:
            all_text += pytesseract.image_to_string(page) + "\n"
        return all_text
    except Exception as e:
        print(f"[OCR Error] {e}")
        return ""


def clean_text(text):
    """Remove non-ASCII chars, fix whitespace."""
    text = text.encode("ascii", errors="ignore").decode("ascii")
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = text.split("\n")
    lines = [l.strip() for l in lines if len(l.strip()) > 3 and not re.match(r'^[\d\s\-_=|]+$', l.strip())]
    return "\n".join(lines)


def extract_syllabus_summary(text, max_chars=2000):
    """
    Build a focused summary: course title + unit topics.
    Capped at 2000 chars to stay within Cohere limits.
    """
    text = clean_text(text)
    collected = []

    # 1. First 400 chars (course title usually here)
    collected.append(text[:400])

    # 2. UNIT headings + first 2 lines of each
    unit_blocks = re.findall(
        r'(UNIT[\s\-]*[IVX\d]+[^\n]*\n(?:[^\n]+\n){0,2})',
        text,
        re.IGNORECASE
    )
    for block in unit_blocks[:6]:
        collected.append(block.strip())

    combined = "\n\n".join(collected)
    return combined[:max_chars]