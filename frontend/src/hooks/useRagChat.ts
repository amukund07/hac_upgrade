import { useState } from 'react';
import { getEmbedding, generateRAGResponse } from '../lib/gemini';

/**
 * THE RAG LOGIC PIPELINE
 * This service handles the orchestration of the RAG process.
 */
export const ragService = {
  /**
   * Performs the full RAG cycle:
   * 1. Embed the user's question.
   * 2. Call the search function to find relevant context.
   * 3. Generate a response using that context.
   * 
   * @param question The user's query
   * @param searchFn A function that takes a vector and returns string snippets from the backend search layer
   */
  async ask(question: string, searchFn: (vector: number[]) => Promise<string[]>) {
    try {
      // Step 1: Get the embedding for the question
      console.log('--- RAG: Step 1: Embedding Question ---');
      const questionVector = await getEmbedding(question);

      // Step 2: Retrieve relevant context from the database-backed search layer
      console.log('--- RAG: Step 2: Retrieving Context ---');
      const relevantContext = await searchFn(questionVector);

      if (!relevantContext || relevantContext.length === 0) {
        console.warn('RAG: No relevant context found in database.');
      }

      // Step 3: Generate the final response using the retrieved context
      console.log('--- RAG: Step 3: Generating Response ---');
      const response = await generateRAGResponse(question, relevantContext);

      return {
        answer: response,
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
