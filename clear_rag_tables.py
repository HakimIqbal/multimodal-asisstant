import mysql.connector
from config import MYSQL_CONFIG

def clear_rag_tables():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Hapus isi tabel
        cursor.execute("TRUNCATE TABLE documents")
        cursor.execute("TRUNCATE TABLE rag_logs")
        cursor.execute("DROP TABLE IF EXISTS ocr_notes")
        
        conn.commit()
        print("System: Berhasil menghapus isi tabel documents, rag_logs, dan ocr_notes (jika ada).")
    except mysql.connector.Error as e:
        print(f"System: Gagal menghapus tabel: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    clear_rag_tables()