import os
import docx
import pdfplumber
from odf import text, teletype
from odf.opendocument import load
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import logging
import io

logging.getLogger("pdfplumber").setLevel(logging.WARNING)

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        return f"❌ Error: File PDF '{pdf_path}' tidak ditemukan."
    text = ""
    try:

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"System: Gagal mengekstrak teks dengan pdfplumber: {str(e)}")


    if not text.strip():
        print(f"System: Tidak ada teks yang terdeteksi dalam {pdf_path} dengan pdfplumber. Mencoba OCR...")
        try:
            # Baca file PDF sebagai bytes
            with open(pdf_path, "rb") as f:
                pdf_content = f.read()
            # Konversi PDF ke gambar
            images = convert_from_bytes(pdf_content)
            for image in images:
                # Ekstrak teks dari gambar menggunakan pytesseract
                page_text = pytesseract.image_to_string(image, lang="eng+ind")
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"System: Gagal mengekstrak teks dengan OCR: {str(e)}")

    return text.strip() or ""

def extract_text_from_docx(docx_path: str) -> str:
    if not os.path.exists(docx_path):
        return f"❌ Error: File DOCX '{docx_path}' tidak ditemukan."
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip() or ""

def extract_text_from_doc(doc_path: str) -> str:
    return extract_text_from_docx(doc_path)  # Asumsi .doc sama dengan .docx

def extract_text_from_odt(odt_path: str) -> str:
    if not os.path.exists(odt_path):
        return f"❌ Error: File ODT '{odt_path}' tidak ditemukan."
    try:
        doc = load(odt_path)
        text_content = []
        for element in doc.getElementsByType(text.P):
            text_content.append(teletype.extractText(element))
        text = "\n".join(text_content)
        return text.strip() or ""
    except Exception as e:
        return f"❌ Error: Gagal mengekstrak teks dari ODT: {str(e)}"

def extract_text_from_txt(txt_path: str) -> str:
    if not os.path.exists(txt_path):
        return f"❌ Error: File TXT '{txt_path}' tidak ditemukan."
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text.strip() or ""
    except Exception as e:
        return f"❌ Error: Gagal mengekstrak teks dari TXT: {str(e)}"

def extract_text(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".doc", ".docx"]:
        return extract_text_from_docx(file_path)
    elif ext == ".odt":
        return extract_text_from_odt(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        return f"❌ Error: Format file '{ext}' tidak didukung."