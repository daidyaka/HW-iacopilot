import "dotenv/config";
import ora from "ora";
import chalk from "chalk";
import readline from "node:readline";
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableBranch, RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { loadNewsDocuments } from "./newsLoader.js";
import { buildVectorStore, retrieveRelevant } from "./retrieval.js";

const spinner = ora("Cargando noticias...");

async function bootstrap() {
  if (!process.env.OPENAI_API_KEY) {
    console.error(
      chalk.red("ERROR: Falta OPENAI_API_KEY. Configure .env o variable de entorno.")
    );
    process.exit(1);
  }

  spinner.start();
  const docs = await loadNewsDocuments();
  await buildVectorStore(docs);
  spinner.succeed(`Noticias cargadas: ${docs.length}`);

  const chat = new ChatOpenAI({ model: "gpt-4o-mini", temperature: 0.2 });

  // Classifier prompt: decide News vs General
  const classifierPrompt = PromptTemplate.fromTemplate(
    `Eres un clasificador. Dado una consulta del usuario, responde exactamente "News" si requiere información de noticias actuales (menciona titulares, hoy, última hora, fuentes CNN/CBC, etc.) o "General" si es conocimiento general.
Consulta: {question}`
  );

  const generalPrompt = PromptTemplate.fromTemplate(
    `Responde de forma útil y concisa a la siguiente consulta general.
Consulta: {question}`
  );

  const newsPrompt = PromptTemplate.fromTemplate(
    `Eres un asistente de noticias. Usa el siguiente contexto extraído de CNN Español y CBC para responder la pregunta del usuario. Si la información no está en el contexto, dilo claramente.

Pregunta: {question}
\nContexto (fragmentos relevantes):\n{context}`
  );

  const toString = new StringOutputParser();

  const classifierChain = RunnableSequence.from([
    classifierPrompt,
    chat,
    toString,
  ]);

  const generalChain = RunnableSequence.from([
    generalPrompt,
    chat,
    toString,
  ]);

  const newsChain = RunnableSequence.from([
    async (input) => {
      const chunks = await retrieveRelevant(input.question, 6);
      const context = chunks.map(c => c.pageContent).join("\n---\n");
      return { ...input, context };
    },
    newsPrompt,
    chat,
    toString,
  ]);

  const decisionChain = RunnableBranch.from([
    [
      async (input) => {
        const decision = await classifierChain.invoke({ question: input.question });
        return decision.trim().toLowerCase().startsWith("news");
      },
      newsChain,
    ],
    generalChain,
  ]);

  // Simple CLI loop with streaming appearance (per-turn execution)
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  console.log(chalk.green("Sistema de Consulta de Noticias listo. Escribe tu pregunta (Ctrl+C para salir)."));

  const ask = () => rl.question(chalk.cyan("› "), async (q) => {
    try {
      const answer = await decisionChain.invoke({ question: q });
      console.log("\n" + chalk.yellow("Respuesta:"));
      console.log(answer + "\n");
    } catch (err) {
      console.error(chalk.red("Error:"), err?.message ?? err);
    }
    ask();
  });

  ask();
}

bootstrap();
