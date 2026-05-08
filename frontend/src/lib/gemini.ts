import { GoogleGenerativeAI } from '@google/generative-ai';

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(API_KEY);

/**
 * 1. EMBEDDING GENERATION
 * Converts text into a vector (768 dimensions) for RAG.
 */
export async function getEmbedding(text: string) {
  const model = genAI.getGenerativeModel({ model: "text-embedding-004" });
  const result = await model.embedContent(text);
  return result.embedding.values;
}

/**
 * 2. RAG GENERATION
 * Takes a user question and a list of retrieved "knowledge snippets".
 * Augments the prompt with this context, prioritizing dadi_story and gen_z_hook for style.
 */
export async function generateRAGResponse(question: string, contextSnippets: string[]) {
  const model = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    systemInstruction: `
      You are the "Wisdom Guide," a bridge between ancient traditional knowledge and modern Gen-Z lifestyle.
      Your tone is:
      - Authentically cultural (like a wise elder or "Dadi").
      - Digitally savvy (understand modern trends and sustainability).
      - Practical and evidence-based (include scientific backing if provided).

      Rules:
      1. Use the provided context to answer. 
      2. If "dadi_story" is available, use its warm, storytelling tone.
      3. If "gen_z_hook" is available, use it to connect with younger audiences.
      4. Always highlight "modern_relevance" or "scientific_backing" to show why this tradition matters today.
      5. If the answer is not in the context, be honest but suggest related wisdom from the context.
    `
  });

  const contextText = contextSnippets.join("\n\n---\n\n");
  const prompt = `
    KNOWLEDGE BASE CONTEXT:
    ${contextText}

    USER QUERY:
    ${question}

    Help the user by applying this traditional wisdom to their modern life.
  `;

  const result = await model.generateContent(prompt);
  return result.response.text();
}

export async function generateLessonNarration(title: string, content: string) {
  const model = genAI.getGenerativeModel({
    model: 'gemini-1.5-flash',
    systemInstruction: `
      You turn lesson content into a warm, natural spoken narration.
      Keep the meaning intact, sound human, and avoid bullet points.
      Aim for 90 to 140 words.
    `,
  });

  const prompt = `
    Lesson title: ${title}
    Lesson content: ${content}

    Rewrite this as a smooth narration a learner can listen to while studying.
  `;

  const result = await model.generateContent(prompt);
  return result.response.text();
}

/**
 * 3. CONTEXTUAL CHAT (Task-Aware)
 * Starts a chat session that is "primed" with the current task's context.
 * This is used for interactive deep-dives while the user is doing an activity.
 */
export function startContextualChat(taskTitle: string, taskContent: string) {
  const model = genAI.getGenerativeModel({
    model: "gemini-1.5-flash",
    systemInstruction: `
      You are an interactive guide for the activity: "${taskTitle}".
      Here is the information the user is currently looking at:
      "${taskContent}"
      
      Your goal:
      - Help the user explore this specific tradition.
      - Connect this tradition to modern sustainability and ethical living.
      - Be encouraging, respectful of indigenous wisdom, and interactive.
    `,
  });

  return model.startChat({
    history: [], // History starts empty, but systemInstruction provides the "soul"
  });
}

/**
 * 4. EMBEDDING MULTIPLE CHUNKS (Batch)
 * Useful for when you have a long story and need to break it into pieces.
 */
export async function embedKnowledgeChunks(chunks: string[]) {
  const model = genAI.getGenerativeModel({ model: "text-embedding-004" });
  const result = await model.batchEmbedContents({
    requests: chunks.map((text) => ({
      content: { role: "user", parts: [{ text }] },
    })),
  });
  return result.embeddings.map((embedding: { values: number[] }) => embedding.values);
}
