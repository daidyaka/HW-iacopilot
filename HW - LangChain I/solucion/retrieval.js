import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { OpenAIEmbeddings } from "@langchain/openai";

let vectorStore; // singleton in process

export async function buildVectorStore(docs) {
  const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-large" });
  vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);
  return vectorStore;
}

export function getVectorStore() {
  if (!vectorStore) throw new Error("Vector store not initialized");
  return vectorStore;
}

export async function retrieveRelevant(query, k = 6) {
  const store = getVectorStore();
  const results = await store.similaritySearch(query, k);
  return results;
}
