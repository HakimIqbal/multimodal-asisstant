import pytesseract
import cv2
import pdfplumber
import os
import docx
import numpy as np
from typing import Optional

# Konfigurasi path Tesseract di macOS
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocessing gambar sebelum OCR untuk meningkatkan akurasi."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold
    processed_img = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )

    return processed_img

def extract_text_from_image(image_path: str) -> str:
    """Membaca teks dari gambar (PNG, JPG, JPEG) menggunakan Tesseract OCR"""
    if not os.path.exists(image_path):
        return f"❌ Error: File gambar '{image_path}' tidak ditemukan."

    try:
        processed_img = preprocess_image(image_path)
        if processed_img is None:
            return "❌ Error: Tidak dapat membaca gambar. Pastikan formatnya benar (PNG, JPG, JPEG)."

        text = pytesseract.image_to_string(processed_img)
        return text.strip() if text.strip() else "⚠️ Tidak ada teks yang terdeteksi dalam gambar."
    except Exception as e:
        return f"❌ Error membaca gambar: {e}"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Membaca teks dari PDF menggunakan pdfplumber"""
    if not os.path.exists(pdf_path):
        return f"❌ Error: File PDF '{pdf_path}' tidak ditemukan."

    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text.strip() if text.strip() else "⚠️ Tidak ada teks yang terdeteksi dalam PDF."
    except Exception as e:
        return f"❌ Error membaca PDF: {e}"

def extract_text_from_docx(docx_path: str) -> str:
    """Membaca teks dari dokumen DOCX"""
    if not os.path.exists(docx_path):
        return f"❌ Error: File DOCX '{docx_path}' tidak ditemukan."

    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip() if text.strip() else "⚠️ Tidak ada teks yang terdeteksi dalam DOCX."
    except Exception as e:
        return f"❌ Error membaca DOCX: {e}"

def extract_text(file_path: str) -> Optional[str]:
    """
    Mendeteksi tipe file dan membaca teks dari gambar (PNG, JPG, JPEG), PDF, atau DOCX.
    """
    if not os.path.exists(file_path):
        return f"❌ Error: File '{file_path}' tidak ditemukan."

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return f"❌ Error: Format file '{ext}' tidak didukung. Gunakan PNG, JPG, PDF, atau DOCX."

# Contoh penggunaan jika dijalankan langsung
if __name__ == "__main__":
    sample_files = {
        "Gambar": "data-rag/documents/contoh-gambar/contoh_gambar.png",
        "PDF": "data-rag/documents/contoh-pdf/contoh_dokumen.pdf",
        "DOCX": "data-rag/documents/contoh-docs/contoh_dokumen.docx"
    }

    for file_type, path in sample_files.items():
        print(f"\n📌 Teks dari {file_type}:")
        print(extract_text(path))
