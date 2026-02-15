
interface SendMessageResponse {
  conversation_id: number;
  response: string;
  tool_calls?: Array<any>;
}

/**
 * Sends a message to the chat API and returns the AI response
 * @param message The user's message to send
 * @param userId The authenticated user's ID (required)
 * @param accessToken The user's authentication token (required)
 * @param conversationId Optional conversation ID for continuing conversations
 * @returns Promise resolving to the AI response
 */
export const sendMessage = async (
  message: string,
  userId: string,  // User ID is required (can be guest ID)
  accessToken: string | null,  // Access token is optional (null for guests)
  conversationId?: string
): Promise<SendMessageResponse> => {

  // Verify that user ID is provided
  if (!userId) {
    throw new Error("User ID is required for chat operations");
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Only add Authorization header if access token is provided
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  // Determine which endpoint to use based on whether we have an access token
  const endpoint = accessToken ?
    `${process.env.NEXT_PUBLIC_API_URL}/api/chat` :
    `${process.env.NEXT_PUBLIC_API_URL}/api/chat/guest`;

  const requestBody: any = {
    message,
    conversation_id: conversationId, // Optional conversation ID for continuing conversations
  };

  // Include user_id in the request if it looks like a guest ID
  if (!accessToken && userId.startsWith('guest_')) {
    requestBody.user_id = userId;
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    headers,
    body: JSON.stringify(requestBody),
  });


  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data;
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
};