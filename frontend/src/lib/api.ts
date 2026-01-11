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

    chatMessage: async (payload: ChatRequest, token: string): Promise<Response> => {
        return fetch(`${API_BASE_URL}/chat/message`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload),
        });
    },

    globalChat: async (payload: GlobalChatRequest, token: string): Promise<Response> => {
        return fetch(`${API_BASE_URL}/chat/global`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload),
        });
    },

    // Auth
    signup: async (email: string, password: string) => {
        return fetchClient<{ user: any, session: any }>("/auth/signup", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });
    },

    login: async (email: string, password: string) => {
        return fetchClient<{ user: any, access_token: string, refresh_token: string }>("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        });
    },

    // Interactions
    addFavorite: async (articleId: number, token: string) => {
        return fetch(`${API_BASE_URL}/interactions/favorites/${articleId}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
    },
    removeFavorite: async (articleId: number, token: string) => {
        return fetch(`${API_BASE_URL}/interactions/favorites/${articleId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
    },
    addReadLater: async (articleId: number, token: string) => {
        return fetch(`${API_BASE_URL}/interactions/read-later/${articleId}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
    },
    removeReadLater: async (articleId: number, token: string) => {
        return fetch(`${API_BASE_URL}/interactions/read-later/${articleId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
    }
};
