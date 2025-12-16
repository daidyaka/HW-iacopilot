import { RecursiveUrlLoader } from "@langchain/community/document_loaders/web/recursive_url";

// Sources
const SOURCES = [
  { url: "https://cnnespanol.cnn.com/lite/", maxDepth: 1 },
  { url: "https://www.cbc.ca/lite/news?sort=latest", maxDepth: 1 }
];

export async function loadNewsDocuments() {
  const docs = [];
  for (const { url, maxDepth } of SOURCES) {
    const loader = new RecursiveUrlLoader(url, {
      maxDepth,
      // Basic filtering: keep typical article paths
      excludeDirs: ["/video", "/podcasts", "/sports"],
      timeout: 20000
    });
    try {
      const loaded = await loader.load();
      docs.push(...loaded);
    } catch (err) {
      console.error("Failed to load", url, err?.message ?? err);
    }
  }
  return docs;
}
