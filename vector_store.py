from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
from interface.contract_interface import store_vector
from pydantic import PrivateAttr
import numpy as np

class BlockchainVectorStore:
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
        self.index = []  # Список кортежей (doc_id, embedding vector)
        self.docs = {}   # Словарь doc_id -> Document

    def add_documents(self, documents):
        MAX_INPUT_LENGTH = 3000  # Максимальная длина текста для эмбеддинга

        for doc in documents:
            content = doc.page_content
            if len(content) > MAX_INPUT_LENGTH:
                content = content[:MAX_INPUT_LENGTH]
            try:
                vec = self.embedding_function.embed_query(content)
            except Exception as e:
                print(f"Error embedding doc {doc.metadata.get('source')}: {e}")
                continue

            int_vec = [int(x * 1000) for x in vec]

            doc_id = doc.metadata.get("source", f"doc_{len(self.index)}")
            store_vector(doc_id, int_vec)
            self.index.append((doc_id, vec))
            self.docs[doc_id] = doc

    def as_retriever(self):
        return BlockchainRetriever(self)


class BlockchainRetriever(BaseRetriever):
    _store: BlockchainVectorStore = PrivateAttr()

    def __init__(self, store: BlockchainVectorStore):
        super().__init__()
        self._store = store

    def get_relevant_documents(self, query):
        query_vec = self._store.embedding_function.embed_query(query)
        query_vec = np.array(query_vec)

        results = []
        for doc_id, vec in self._store.index:
            vec_np = np.array(vec)
            sim = np.dot(query_vec, vec_np) / (np.linalg.norm(query_vec) * np.linalg.norm(vec_np))
            results.append((sim, doc_id))

        results.sort(key=lambda x: x[0], reverse=True)

        return [
            self._store.docs[doc_id]
            for _, doc_id in results[:3]
            if doc_id in self._store.docs
        ]


def get_db():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return BlockchainVectorStore(embedding_function=embeddings)