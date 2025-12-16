import os
import pytest
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA


@pytest.fixture(scope="session")
def setup_rag():
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY debe estar configurada"
    llm = ChatOpenAI(model="gpt-4o-mini")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local("./index", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(k=2)
    return llm, retriever


def test_csv_balance():
    import pandas as pd
    df = pd.read_csv("../data/saldos.csv")
    assert not df.empty, "saldos.csv no debe estar vacío"
    sample_id = df.iloc[0]["ID_Cedula"]
    assert isinstance(sample_id, str)


def test_knowledge_base_query(setup_rag):
    llm, retriever = setup_rag
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, verbose=False)
    resp = chain.invoke({"query": "Como abro una cuenta de ahorros en el banco?"})
    assert "result" in resp and isinstance(resp["result"], str)


def test_general_llm(setup_rag):
    llm, _ = setup_rag
    out = llm.invoke("Cual es el sentido de la vida?")
    assert hasattr(out, "content") and isinstance(out.content, str)
