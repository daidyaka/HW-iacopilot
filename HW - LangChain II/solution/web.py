from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.tools import tool

_ = load_dotenv(find_dotenv())

llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local("./index", embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(k=2)

@tool
def get_balance_by_id(cedula_id: str) -> str:
    import pandas as pd
    df = pd.read_csv("../data/saldos.csv")
    matches = df[df["ID_Cedula"] == cedula_id]
    if matches.empty:
        return "No se encontró balance para esa cédula."
    return str(matches["Balance"].values[0])

@tool
def get_bank_information(question: str) -> str:
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, verbose=False)
    resp = chain.invoke({"query": question})
    return resp["result"]

tools = [get_balance_by_id, get_bank_information]
agent = create_react_agent(llm, tools, prompt=hub.pull("hwchase17/react"))
agent_executor = AgentExecutor(agent=agent, tools=tools)

app = FastAPI()

class AskBody(BaseModel):
    question: str

@app.post("/ask")
def ask(body: AskBody):
    result = agent_executor.invoke({"input": body.question})
    return {"answer": result.get("output", result)}

@app.get("/")
def home():
        return (
                """
                <html>
                    <head><title>Banco Assistant</title></head>
                    <body style="font-family: sans-serif; max-width: 720px; margin: 2rem auto;">
                        <h2>Sistema de Atención al Cliente</h2>
                        <p>Escribe una pregunta y presiona Enviar.</p>
                        <form onsubmit="event.preventDefault(); send();">
                            <textarea id="q" rows="4" style="width:100%" placeholder="Ej: Cual es el balance de la cuenta de la cedula V-91827364?"></textarea>
                            <br/><br/>
                            <button type="submit">Enviar</button>
                        </form>
                        <h3>Respuesta</h3>
                        <pre id="ans" style="white-space: pre-wrap"></pre>
                        <script>
                            async function send() {
                                const q = document.getElementById('q').value;
                                const res = await fetch('/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) });
                                const data = await res.json();
                                document.getElementById('ans').textContent = data.answer;
                            }
                        </script>
                    </body>
                </html>
                """
        )
