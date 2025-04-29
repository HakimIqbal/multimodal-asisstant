# Multimodal Assistant

Asisten AI dengan fitur General Chat, Coder Chat, RAG System (Chat Dokumen), dan OCR.

## Fitur
- **General Chat**: Tanyakan apa saja secara umum.
- **Coder Chat**: Tanyakan hal terkait coding (debugging, penjelasan kode, dll).
- **RAG System (Chat Dokumen)**: Unggah dokumen (DOC, DOCX, PDF maks 10MB) untuk menjawab pertanyaan berdasarkan konten dokumen.
- **OCR**: Ekstrak teks dari gambar (JPG, PNG, HEIC, JPEG, SVG, maks 5MB) dan jawab pertanyaan berdasarkan teks tersebut.


---

### **Langkah-Langkah Menjalankan Proyek**

1. **Instal Prasyarat**:
   - Python 3.8+.
   - MySQL (pastikan server berjalan).
   - Tesseract OCR (`brew install tesseract` di Mac, atau instal di Windows/Linux).
   - Poppler (`brew install poppler` di Mac, atau instal di Windows/Linux).

2. **Konfigurasi MySQL**:
   - Instal MySQL jika belum ada (`brew install mysql` di Mac, atau unduh dari mysql.com).
   - Buat database:
     ```bash
     mysql -u root -p
     CREATE DATABASE multimodal_assistant;
     ```
   - Jalankan skrip SQL dari README.md untuk membuat tabel.

3. **Konfigurasi TablePlus**:
   - Unduh dan instal TablePlus dari https://tableplus.com/.
   - Buat koneksi baru dengan detail dari `.env` (host, user, password, database).
   - Test koneksi dan jalankan skrip SQL.

4. **Setup Proyek**:
   - Clone repository atau buat struktur folder seperti di atas.
   - Salin kode ke masing-masing file.
   - Buat file `.env` dan isi sesuai contoh.
   - Instal dependensi:
     ```bash
     pip install -r requirements.txt
     ```

5. **Jalankan Aplikasi**:
   - Jalankan API:
     ```bash
     python main.py
     ```
   - Jalankan UI:
     ```bash
     streamlit run app.py
     ```

6. **Uji Fitur**:
   - Buka `http://localhost:8501` untuk UI.
   - Uji General Chat, Coder Chat, RAG Chat, OCR, dan Upload Dokumen.
   - Gunakan Postman atau curl untuk menguji API.

---

### **Catatan Tambahan**
- **Error Handling**: Kode telah diuji untuk mencegah error umum (file tidak ditemukan, format tidak didukung, dll).
- **Integrasi**: API menggunakan FastAPI dengan CORS, cocok untuk website dan mobile.
- **Skalabilitas**: MySQL lokal cocok untuk pengembangan, tetapi untuk produksi, pertimbangkan cloud database.
- **Keamanan**: Pastikan password MySQL aman dan `.env` tidak diunggah ke repositori publik.

Jika ada pertanyaan atau perlu bantuan lebih lanjut, silakan beri tahu!