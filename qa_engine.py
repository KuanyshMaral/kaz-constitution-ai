from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

def answer_query(query, db):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever(),
        return_source_documents=True
    )

    result = qa_chain.invoke({"query": query})
    return result["result"]