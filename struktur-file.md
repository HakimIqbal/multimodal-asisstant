/multimodal-assistant/
├── main.py
├── models.py
├── app.py
├── config.py
├── requirements.txt
├── data-rag/
│   ├── documents/
│   │   ├── pdf/
│   │   ├── doc/
│   │   ├── docx/
│   │   ├── odt/
│   │   ├── txt/
│   ├── faiss_index/
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── logs/
│       └── archive/
├── data-ocr/
│   └── logs/
│       └── archive/
├── src/
│   ├── __init__.py
│   ├── ocr.py
│   ├── rag.py
│   ├── vector_db.py
│   ├── chat.py
│   ├── coder.py
│   ├── db.py
│   ├── document_processor.py
├── api/
│   ├── server.py
│   └── endpoints/
│       ├── chat.py
│       ├── coder.py
│       ├── rag.py
│       ├── ocr.py
├── migrations/
│   ├── init.sql
├── .env