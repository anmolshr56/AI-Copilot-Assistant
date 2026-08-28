import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from backend.llm_config import get_llm

embeddings = OllamaEmbeddings(model="gemma2:2b")

DB_DIR = "data/chroma_db"

RAG_PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end.

If you don't know the answer, just say that you don't know.

Context:
{context}

Question:
{question}

Helpful Answer:
"""

def ingest_pdf(file_path):

    if os.path.exists(DB_DIR):
        try:
            shutil.rmtree(DB_DIR)
        except:
            pass

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    texts = text_splitter.split_documents(documents)

    return Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

def get_chat_response(query, use_cloud=False):

    if not os.path.exists(DB_DIR):
        return "Please upload a PDF first."

    vectorstore = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )

    llm = get_llm(use_cloud=use_cloud)

    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain.invoke(query)["result"]