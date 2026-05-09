import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

/**
 * THE RAG LOGIC PIPELINE
 * This service handles the orchestration of the RAG process.
 */
export const ragService = {
  /**
   * Performs the full RAG cycle:
   * 1. Call the search function to find relevant context (usually via backend).
   * 2. Generate a response using that context via backend Gemini.
   * 
   * @param question The user's query
   * @param searchFn A function that returns string snippets
   */
  async ask(question: string, searchFn: (vector: number[]) => Promise<string[]>) {
    try {
      // NOTE: For true RAG, we need embeddings. 
      // Since we moved to backend, we can either:
      // 1. Send the question to a backend /api/gemini/rag endpoint that does the embedding + search.
      // 2. Keep the current structure but call backend for generation.
      
      // Step 1: Retrieve context (this usually involves an embedding step inside searchFn or similar)
      console.log('--- RAG: Retrieving Context ---');
      const relevantContext = await searchFn([]); // Empty vector for now if searchFn handles it

      // Step 2: Generate response via backend
      console.log('--- RAG: Generating Response via Backend ---');
      const response = await fetch(`${API_BASE}/gemini`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'rag', question, contextSnippets: relevantContext }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate RAG response')
      }

      const payload = await response.json() as { data: { response: string } }

      return {
        answer: payload.data.response,
        contextUsed: relevantContext,
      };
    } catch (error) {
      console.error('RAG Pipeline Error:', error);
      throw error;
    }
  }
};

/**
 * REACT HOOK: useRagChat
 * Makes it easy to use RAG in your UI components.
 */
export function useRagChat() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = async (
    question: string, 
    searchFn: (vector: number[]) => Promise<string[]>
  ) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await ragService.ask(question, searchFn);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { askQuestion, isLoading, error };
}
