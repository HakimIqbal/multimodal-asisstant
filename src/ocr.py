import pytesseract
import cv2
import pdfplumber
import os

# Konfigurasi Tesseract untuk macOS (gunakan path yang benar)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def extract_text_from_image(image_path: str) -> str:
    """Membaca teks dari gambar menggunakan Tesseract OCR"""
    if not os.path.exists(image_path):
        return f"Error: File gambar '{image_path}' tidak ditemukan."

    try:
        image = cv2.imread(image_path)
        if image is None:
            return "Error: Tidak dapat membaca gambar. Pastikan formatnya benar."

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Konversi ke grayscale
        text = pytesseract.image_to_string(gray)
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

# Contoh penggunaan
if __name__ == "__main__":
    image_path = "data-rag/contoh-gambar/contoh_gambar.png"
    pdf_path = "data-rag/contoh-pdf/contoh_dokumen.pdf"

    image_text = extract_text_from_image(image_path)
    print("Teks dari Gambar:\n", image_text)

    pdf_text = extract_text_from_pdf(pdf_path)
    print("\nTeks dari PDF:\n", pdf_text)
