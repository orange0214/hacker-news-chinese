import { useState, useRef } from 'react';
import { ChatMessage, ChatRequest, GlobalChatRequest } from '@/types/api';
import { api } from '@/lib/api';

export function useChatStream() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = async (
        content: string,
        mode: 'global' | 'article',
        articleId?: number
    ) => {
        setIsLoading(true);
        const userMessage: ChatMessage = { role: 'user', content };
        setMessages(prev => [...prev, userMessage]);

        // Add temporary assistant placeholder
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        let response: Response;
        const history = messages.map(({ role, content }) => ({ role, content }));
        history.push(userMessage);

        try {
            if (mode === 'article' && articleId) {
                response = await api.chatMessage({ article_id: articleId, message: content, history });
            } else {
                response = await api.globalChat({ message: content, history });
            }

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessageContent = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                assistantMessageContent += chunk;

                // Update the last message (assistant's placeholder)
                setMessages(prev => {
                    const newMessages = [...prev];
                    newMessages[newMessages.length - 1] = {
                        role: 'assistant',
                        content: assistantMessageContent
                    };
                    return newMessages;
                });
            }

        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'assistant', content: "Error: Failed to fetch response." }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const resetChat = () => setMessages([]);

    return { messages, isLoading, sendMessage, resetChat };
}
