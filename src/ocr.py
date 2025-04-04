import pytesseract
import cv2
import pdfplumber
import os
import docx
from typing import Optional

# Konfigurasi Tesseract untuk macOS (gunakan path yang benar)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def extract_text_from_image(image_path: str) -> str:
    """Membaca teks dari gambar (PNG, JPG, JPEG) menggunakan Tesseract OCR"""
    if not os.path.exists(image_path):
        return f"Error: File gambar '{image_path}' tidak ditemukan."

    try:
        # Baca gambar
        image = cv2.imread(image_path)
        if image is None:
            return "Error: Tidak dapat membaca gambar. Pastikan formatnya benar (PNG, JPG, JPEG)."

        # Konversi ke grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Adaptive Thresholding untuk meningkatkan akurasi OCR
        processed_img = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )

        # Ekstrak teks menggunakan Tesseract OCR
        text = pytesseract.image_to_string(processed_img)
        return text.strip() if text.strip() else "Tidak ada teks yang terdeteksi dalam gambar."
    except Exception as e:
        return f"Error membaca gambar: {e}"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Membaca teks dari PDF menggunakan pdfplumber"""
    if not os.path.exists(pdf_path):
        return f"Error: File PDF '{pdf_path}' tidak ditemukan."

    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # Hindari None
                    text += page_text + "\n"
        return text.strip() if text.strip() else "Tidak ada teks yang terdeteksi dalam PDF."
    except Exception as e:
        return f"Error membaca PDF: {e}"

def extract_text_from_docx(docx_path: str) -> str:
    """Membaca teks dari dokumen DOCX"""
    if not os.path.exists(docx_path):
        return f"Error: File DOCX '{docx_path}' tidak ditemukan."

    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip() if text.strip() else "Tidak ada teks yang terdeteksi dalam DOCX."
    except Exception as e:
        return f"Error membaca DOCX: {e}"

def extract_text(file_path: str) -> Optional[str]:
    """
    Mendeteksi tipe file dan membaca teks dari gambar (PNG, JPG, JPEG), PDF, atau DOCX.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' tidak ditemukan."

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return f"Error: Format file '{ext}' tidak didukung. Gunakan PNG, JPG, PDF, atau DOCX."

# Contoh penggunaan jika dijalankan langsung
if __name__ == "__main__":
    image_path = "data-rag/contoh-gambar/contoh_gambar.jpg"
    pdf_path = "data-rag/contoh-pdf/contoh_dokumen.pdf"
    docx_path = "data-rag/contoh-docx/contoh_dokumen.docx"

    print("📌 Teks dari Gambar:\n", extract_text(image_path))
    print("\n📌 Teks dari PDF:\n", extract_text(pdf_path))
    print("\n📌 Teks dari DOCX:\n", extract_text(docx_path))
