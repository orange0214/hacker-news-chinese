import { create } from 'zustand';

interface ChatState {
    isOpen: boolean;
    mode: 'global' | 'article';
    articleId?: number;
    articleTitle?: string;
    openChat: (mode: 'global' | 'article', articleId?: number, articleTitle?: string) => void;
    closeChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
    isOpen: false,
    mode: 'global',
    articleId: undefined,
    articleTitle: undefined,
    openChat: (mode, articleId, articleTitle) => set({ isOpen: true, mode, articleId, articleTitle }),
    closeChat: () => set({ isOpen: false, articleId: undefined, articleTitle: undefined }),
}));
