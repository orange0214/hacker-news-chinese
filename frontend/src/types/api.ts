export interface AITranslatedResult {
    topic: string;
    title_cn: string;
    summary: string;
    key_points: string[];
    tech_stack: string[];
    takeaway: string;
    ai_score: number;
    original_text_trans?: string;
    url_content_trans?: string;
}

export interface ArticleSchema {
    id: number;
    hn_id: number;
    original_title: string;
    original_url?: string;
    original_text?: string;
    score: number;
    posted_at: string; // ISO Date string
    by?: string;
    type: string;
    detailed_analysis?: AITranslatedResult;
    descendants?: number;
    deleted?: boolean;
    dead?: boolean;
}

export interface ArticleListResponse {
    items: ArticleSchema[];
    total: number;
    page: number;
    size: number;
    total_pages: number;
}

export enum SortField {
    POSTED_AT = "posted_at",
    SCORE = "score",
    AI_SCORE = "ai_score",
}

export enum SortOrder {
    DESC = "desc",
    ASC = "asc",
}

export interface ArticleFilterParams {
    page?: number;
    size?: number;
    sort_by?: SortField;
    order?: SortOrder;
}

export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

export interface ConversationSchema {
    id: string;
    title?: string;
    article_id?: number;
    updated_at: string;
}

export interface ConversationMessageSchema extends ConversationSchema {
    messages: ChatMessage[];
}

export interface ChatRequest {
    article_id: number;
    message: string;
    conversation_id?: string;
}

export interface GlobalChatRequest {
    message: string;
    conversation_id?: string;
}
