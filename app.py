import os
import shutil

# Очистка базы перед запуском
persist_directory = "chroma_db"
if os.path.exists(persist_directory):
    try:
        shutil.rmtree(persist_directory)
        print("✅ Хранилище очищено")
    except Exception as e:
        print(f"❌ Не удалось удалить базу: {e}")

import streamlit as st
from document_loader import process_and_store_file, process_and_store_url
from vector_store import get_db
from qa_engine import answer_query

st.set_page_config(page_title="Kazakhstan Constitution AI Assistant")
st.title("🇰🇿 Constitution of Kazakhstan - AI Assistant")

# Глобальное хранилище, создаётся заново при запуске
db = get_db()

# Загрузка файлов
uploaded_files = st.file_uploader("Upload PDF or TXT files", accept_multiple_files=True)

# Ввод URL сайтов
urls_input = st.text_area("Or enter website URLs (one per line):")

if uploaded_files:
    for uploaded_file in uploaded_files:
        process_and_store_file(uploaded_file, db)
    st.success("Files processed and stored successfully.")

if urls_input:
    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
    for url in urls:
        try:
            process_and_store_url(url, db)
        except Exception as e:
            st.error(f"Error processing URL {url}: {e}")
    st.success("URLs processed and stored successfully.")

# Ввод вопроса
query = st.text_input("Ask a question about the Constitution or your uploaded documents:")
if query:
    response = answer_query(query, db)
    st.markdown("### 🤖 Answer")
    st.write(response)