from langchain.vectorstores import Chroma
import os
import shutil
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_db():
    persist_directory = "chroma_db"
    if os.path.exists(persist_directory):
        try:
            shutil.rmtree(persist_directory)
        except Exception as e:
            print(f"Не удалось удалить базу: {e}")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)