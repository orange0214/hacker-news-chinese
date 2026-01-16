"use client";

import { useChatStore } from "@/stores/chat";
import { useChatStream } from "@/hooks/use-chat-stream";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SendIcon, Loader2Icon, Sparkles } from "lucide-react";
import { ChatMessageBubble } from "./chat-message-bubble";
import { useState, useEffect, useRef } from "react";

import { LoginForm } from "./login-form";
import { useAuthStore } from "@/stores/auth";

import { usePathname } from "next/navigation";

export function ChatPanel() {
    const { isOpen, closeChat, mode, articleId, articleTitle } = useChatStore();
    const { messages, isLoading, sendMessage, resetChat } = useChatStream();
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);
    const token = useAuthStore((state) => state.token);
    const pathname = usePathname();

    // Auto-close chat on navigation (route change)
    useEffect(() => {
        if (isOpen) {
            closeChat();
        }
    }, [pathname]);

    // Reset chat when opening a new session
    useEffect(() => {
        if (isOpen) {
            resetChat();
        }
    }, [isOpen, articleId, mode]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;
        sendMessage(input, mode, articleId);
        setInput("");
    };

    return (
        <Sheet open={isOpen} onOpenChange={(open) => !open && closeChat()} modal={false}>
            <SheetContent
                className="w-full sm:w-[450px] flex flex-col p-0 border-l border-border/40 bg-background/95 backdrop-blur-3xl shadow-2xl"
                side="right"
                disableOverlay={true}
            >
                <SheetHeader className="p-4 border-b border-border/40">
                    <SheetTitle className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-indigo-400" />
                        {mode === 'global' ? "Global AI Chat" : "Article Assistant"}
                    </SheetTitle>
                    <SheetDescription className="truncate">
                        {mode === 'global'
                            ? "Ask me anything across all Hacker News stories."
                            : `Discussing: ${articleTitle || 'this article'}`
                        }
                    </SheetDescription>
                </SheetHeader>

                {!token ? (
                    <LoginForm />
                ) : (
                    <>
                        <ScrollArea className="flex-grow p-4 bg-transparent">
                            <div className="flex flex-col gap-2 min-h-full justify-end">
                                {messages.length === 0 && (
                                    <div className="flex flex-col items-center justify-center flex-grow text-muted-foreground opacity-50 space-y-2 py-10">
                                        <Sparkles className="w-10 h-10" />
                                        <p className="text-sm">Start the conversation...</p>
                                    </div>
                                )}
                                {messages.map((msg, idx) => (
                                    <ChatMessageBubble key={idx} message={msg} />
                                ))}
                                {isLoading && (
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground ml-2 animate-pulse">
                                        <Loader2Icon className="w-3 h-3 animate-spin" />
                                        Thinking...
                                    </div>
                                )}
                                <div ref={scrollRef} />
                            </div>
                        </ScrollArea>

                        <div className="p-4 border-t border-border/40 bg-muted/10">
                            <form onSubmit={handleSubmit} className="flex gap-2">
                                <Input
                                    value={input}
                                    onChange={e => setInput(e.target.value)}
                                    placeholder="Ask a question..."
                                    className="bg-background/50 border-border/50 focus-visible:ring-indigo-500/50"
                                    disabled={isLoading}
                                />
                                <Button type="submit" size="icon" disabled={isLoading || !input.trim()} className="shrink-0 bg-indigo-600 hover:bg-indigo-700">
                                    {isLoading ? <Loader2Icon className="w-4 h-4 animate-spin" /> : <SendIcon className="w-4 h-4" />}
                                </Button>
                            </form>
                        </div>
                    </>
                )}
            </SheetContent>
        </Sheet>
    );
}
