import { ArticleFilterParams, ArticleListResponse, ChatRequest, GlobalChatRequest } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!res.ok) {
        const errorBody = await res.text();
        throw new Error(`API Error ${res.status}: ${errorBody}`);
    }

    return res.json();
}

export const api = {
    getArticles: async (params: ArticleFilterParams): Promise<ArticleListResponse> => {
        const query = new URLSearchParams();
        if (params.page) query.set("page", params.page.toString());
        if (params.size) query.set("size", params.size.toString());
        if (params.sort_by) query.set("sort_by", params.sort_by);
        if (params.order) query.set("order", params.order);

        return fetchClient<ArticleListResponse>(`/articles/?${query.toString()}`);
    },

    chatMessage: async (payload: ChatRequest): Promise<Response> => {
        // Returning Response object for streaming handling in component
        return fetch(`${API_BASE_URL}/chat/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    },

    globalChat: async (payload: GlobalChatRequest): Promise<Response> => {
        return fetch(`${API_BASE_URL}/chat/global`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
    },
};
