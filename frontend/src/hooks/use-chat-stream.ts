import { useState } from 'react';
import { ChatMessage } from '@/types/api';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/auth';

export function useChatStream() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | undefined>(undefined);
    const token = useAuthStore((state) => state.token);

    const sendMessage = async (
        content: string,
        mode: 'global' | 'article',
        articleId?: number
    ) => {
        if (!token) {
            setMessages(prev => [...prev, { role: 'user', content }]);
            setTimeout(() => {
                setMessages(prev => [...prev, { role: 'assistant', content: "Please sign in to use the chat." }]);
            }, 200);
            return;
        }

        setIsLoading(true);
        const userMessage: ChatMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);

        // Add temporary assistant placeholder
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        let response: Response;

        try {
            if (mode === 'article' && articleId) {
                response = await api.chatMessage({ article_id: articleId, message: content, conversation_id: conversationId }, token);
            } else {
                response = await api.globalChat({ message: content, conversation_id: conversationId }, token);
            }

            if (!response.body) throw new Error("No response body");
            if (response.status === 401) throw new Error("Unauthorized. Please sign in again.");
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessageContent = "";
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;

                const lines = buffer.split("\n\n");
                buffer = lines.pop() || ""; // Keep the last incomplete chunk

                for (const line of lines) {
                    if (line.startsWith("event: new_conversation")) {
                        const dataLine = line.split("\n")[1];
                        if (dataLine?.startsWith("data: ")) {
                            const newId = dataLine.replace("data: ", "").trim();
                            setConversationId(newId);
                        }
                    } else if (line.startsWith("data: ")) {
                        const data = line.replace("data: ", "");
                        if (data === "[DONE]") continue;

                        // Backend replaces \n with \\n, we need to reverse it
                        const text = data.replace(/\\n/g, "\n");
                        assistantMessageContent += text;

                        setMessages(prev => {
                            const newMessages = [...prev];
                            newMessages[newMessages.length - 1] = {
                                role: 'assistant',
                                content: assistantMessageContent
                            };
                            return newMessages;
                        });
                    } else if (line.startsWith("event: error")) {
                        const dataLine = line.split("\n")[1];
                        const error = dataLine?.replace("data: ", "") || "Unknown error";
                        throw new Error(error);
                    }
                }
            }

        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'assistant', content: `Error: ${error instanceof Error ? error.message : 'Failed to fetch response.'}` }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const resetChat = () => {
        setMessages([]);
        setConversationId(undefined);
    };

    return { messages, isLoading, sendMessage, resetChat };
}
