import tempfile
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

def get_text_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = '\n'.join(p.get_text() for p in paragraphs if p.get_text().strip())
    return text

def process_and_store_file(uploaded_file, db):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        file_path = tmp.name

    if uploaded_file.name.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding='utf-8')

    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    db.add_documents(docs)

def process_and_store_url(url: str, db):
    text = get_text_from_url(url)

    # Уменьшаем размер чанков для URL, чтобы не превышать лимит API
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_text(text)

    MAX_CHUNK_LENGTH = 3000  # Максимальная длина текста для эмбеддинга

    docs = []
    for chunk in chunks:
        if len(chunk) > MAX_CHUNK_LENGTH:
            chunk = chunk[:MAX_CHUNK_LENGTH]
        docs.append(Document(page_content=chunk, metadata={"source": url}))

    db.add_documents(docs)