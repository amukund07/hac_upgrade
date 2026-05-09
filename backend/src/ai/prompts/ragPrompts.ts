/**
 * RAG Prompt Templates
 * Carefully engineered prompts for grounded AI responses
 */

import { IRetrievedSource } from '../../models/ChatHistory'

/**
 * Main RAG system prompt - instructions for the AI
 */
export const RAG_SYSTEM_PROMPT = `You are "Wisdom Guide," a bridge between ancient traditional knowledge and modern Gen-Z life.

Your role: Answer questions ONLY based on the provided knowledge context. Never invent cultural facts.

Personality:
- Wise elder or "Dadi" - warm, authentic, respectful
- Digitally savvy - understand modern trends, Gen-Z language
- Practical and evidence-based - include scientific backing when available
- Cultural champion - honor traditions while making them relevant today

Core Rules:
1. GROUND ALL ANSWERS IN PROVIDED CONTEXT - This is non-negotiable
2. If context is insufficient, say "I don't have enough knowledge about this" rather than guessing
3. Use storytelling when available (dadi_story fields) to make concepts memorable
4. Connect to modern life (modern_relevance fields) to show why this matters today
5. Include scientific backing when available to build credibility
6. Avoid hallucinating cultural facts - accuracy over elaboration
7. Keep responses concise but meaningful (2-4 paragraphs for most questions)
8. Use Hindi/Sanskrit terms occasionally with English explanations for cultural authenticity
9. Encourage respect for traditions and science together
10. When appropriate, suggest practical applications in daily life

Tone Guidelines:
- Warm and inclusive (like teaching a younger generation)
- Respectful of both ancient wisdom and modern science
- Practical and actionable
- Never preachy or judgmental

Response Format:
- Start with a direct answer to the question
- Use storytelling elements if relevant
- Include scientific/practical context
- End with connection to modern life or a takeaway`

/**
 * Build knowledge context string from retrieved sources
 */
export const buildKnowledgeContext = (sources: IRetrievedSource[]): string => {
  if (sources.length === 0) {
    return 'No relevant knowledge found in the database.'
  }

  const contextParts = sources.map((source, index) => {
    return `[Source ${index + 1} - ${source.domain}${source.title ? `: ${source.title}` : ''}]
${source.content}
Relevance Score: ${(source.similarity * 100).toFixed(1)}%`
  })

  return `TRADITIONAL KNOWLEDGE BASE CONTEXT:

${contextParts.join('\n\n---\n\n')}

---

Use the above context to answer the user's question. Only reference information that appears in the context.`
}

/**
 * Build the full prompt for RAG query
 */
export const buildRAGPrompt = (
  userQuery: string,
  retrievedContext: string,
  sessionInfo?: { previousTurns?: number; domain?: string }
): string => {
  let prompt = `${retrievedContext}

USER QUESTION:
${userQuery}`

  if (sessionInfo?.previousTurns && sessionInfo.previousTurns > 0) {
    prompt += `

[Note: This is turn ${sessionInfo.previousTurns + 1} in the conversation. Maintain context from previous exchanges while answering this new question.]`
  }

  if (sessionInfo?.domain) {
    prompt += `

[Focus Area: ${sessionInfo.domain}]`
  }

  prompt += `

Please provide a helpful, grounded answer based only on the traditional knowledge provided above.`

  return prompt
}

/**
 * Build a follow-up prompt when no relevant context is found
 */
export const buildFallbackPrompt = (userQuery: string): string => {
  return `${RAG_SYSTEM_PROMPT}

IMPORTANT: You do not have specific traditional knowledge about this topic in your database. 

However, you can provide a helpful response by:
1. Explaining what kind of traditional knowledge might apply
2. Suggesting related areas of wisdom that ARE in your knowledge base
3. Encouraging the user to explore those related topics
4. Never making up specific cultural facts, remedies, or practices

USER QUESTION:
${userQuery}

Provide a thoughtful response that guides them without making up information.`
}

/**
 * Build context injection for better Gemini understanding
 */
export const buildContextInjectionPrompt = (
  userQuery: string,
  sources: IRetrievedSource[],
  isFollowUp: boolean = false
): { system: string; user: string } => {
  const knowledgeContext = buildKnowledgeContext(sources)
  const sessionInfo = isFollowUp
    ? { previousTurns: 1, domain: sources[0]?.domain }
    : undefined

  return {
    system: RAG_SYSTEM_PROMPT,
    user: buildRAGPrompt(userQuery, knowledgeContext, sessionInfo),
  }
}

/**
 * Build error handling prompt
 */
export const buildErrorRecoveryPrompt = (
  userQuery: string,
  errorMessage: string
): { system: string; user: string } => {
  return {
    system: RAG_SYSTEM_PROMPT,
    user: `I encountered an issue retrieving context, but I'll still try to help with your question using general traditional wisdom:

USER QUESTION:
${userQuery}

ERROR CONTEXT: ${errorMessage}

Please provide a helpful response based on general knowledge, but note that I couldn't pull specific sources this time.`,
  }
}

/**
 * Build conversation summary prompt for context preservation
 */
export const buildConversationSummary = (
  previousQuery: string,
  previousResponse: string,
  currentQuery: string
): string => {
  return `Previous context in this conversation:
Q: ${previousQuery}
A: ${previousResponse}

Now the user asks: ${currentQuery}

Keep the previous context in mind while answering this follow-up question.`
}
