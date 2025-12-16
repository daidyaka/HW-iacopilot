from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from dotenv import load_dotenv, find_dotenv
import sys

_ = load_dotenv(find_dotenv())  # read local .env file


llm = ChatOpenAI(model="gpt-4o-mini")

embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

db = FAISS.load_local(
    "./index",
    embeddings,
    allow_dangerous_deserialization=True,
)
retriever = db.as_retriever(k=2)


@tool
def get_balance_by_id(cedula_id: str) -> str:
    """Obtiene balance de la cuenta por cedula_id (CSV)."""
    import pandas as pd
    df = pd.read_csv("../data/saldos.csv")
    matches = df[df["ID_Cedula"] == cedula_id]
    if matches.empty:
        return "No se encontró balance para esa cédula."
    return str(matches["Balance"].values[0])


@tool
def get_bank_information(question: str) -> str:
    """Información bancaria vía RAG (FAISS + KB)."""
    bank_info_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=False,
    )
    response = bank_info_chain.invoke({"query": question})
    return response["result"]


tools = [get_balance_by_id, get_bank_information]


def build_agent_executor():
    agent = create_react_agent(llm, tools, prompt=hub.pull("hwchase17/react"))
    return AgentExecutor(agent=agent, tools=tools)


def main():
    agent_executor = build_agent_executor()
    print("Sistema de Atención al Cliente listo. Escribe tu pregunta (Ctrl+C para salir).")
    try:
        while True:
            inp = input("› ")
            result = agent_executor.invoke({"input": inp})
            print("\nRespuesta:\n" + str(result.get("output", result)) + "\n")
    except KeyboardInterrupt:
        print("\nHasta luego!")


if __name__ == "__main__":
    # Allow one-off question via CLI args
    if len(sys.argv) > 1:
        agent_executor = build_agent_executor()
        question = " ".join(sys.argv[1:])
        result = agent_executor.invoke({"input": question})
        print(result.get("output", result))
    else:
        main()
