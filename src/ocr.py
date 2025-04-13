import pytesseract
import cv2
import pdfplumber
import os
import docx
import numpy as np
from typing import Optional
import logging

logging.getLogger("pdfplumber").setLevel(logging.ERROR)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def preprocess_image(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    processed_img = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )
    return processed_img

def extract_text_from_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return f"❌ Error: File gambar '{image_path}' tidak ditemukan."
    image = cv2.imread(image_path)
    if image is None:
        return "❌ Error: Tidak dapat membaca gambar."
    height, width = image.shape[:2]
    if height < 100 or width < 100:
        return "⚠️ Tidak ada teks yang terdeteksi dalam gambar. Gambar memiliki resolusi terlalu rendah."
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img)
    return text.strip() or "⚠️ Tidak ada teks yang terdeteksi dalam gambar. Coba gunakan gambar dengan teks yang lebih jelas."

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        return f"❌ Error: File PDF '{pdf_path}' tidak ditemukan."
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip() or "⚠️ Tidak ada teks yang terdeteksi dalam PDF."

def extract_text_from_docx(docx_path: str) -> str:
    if not os.path.exists(docx_path):
        return f"❌ Error: File DOCX '{docx_path}' tidak ditemukan."
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip() or "⚠️ Tidak ada teks yang terdeteksi dalam DOCX."

def extract_text(file_path: str) -> Optional[str]:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return f"❌ Error: Format file '{ext}' tidak didukung."