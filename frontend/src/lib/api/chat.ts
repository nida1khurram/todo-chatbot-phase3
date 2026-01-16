
interface SendMessageResponse {
  conversation_id: number;
  response: string;
  tool_calls?: Array<any>;
}

/**
 * Sends a message to the chat API and returns the AI response
 * @param message The user's message to send
 * @param accessToken The user's authentication token
 * @returns Promise resolving to the AI response
 */
export const sendMessage = async (
  message: string,
  userId: string = "guest",
  accessToken: string = "",
  conversationId?: string
): Promise<SendMessageResponse> => {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Add authorization header only if token is provided
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message,
        conversation_id: conversationId, // Optional conversation ID for continuing conversations
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

/**
 * Gets conversation history for a specific conversation
 * @param conversationId The ID of the conversation to retrieve
 * @param accessToken The user's authentication token
 * @returns Promise resolving to the conversation history
 */
export const getConversationHistory = async (
  userId: string,
  conversationId: number,
  accessToken: string
): Promise<any> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/conversations/${conversationId}/history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting conversation history:', error);
    throw error;
  }
};