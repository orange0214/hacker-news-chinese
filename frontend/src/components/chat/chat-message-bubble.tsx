import { ChatMessage } from "@/types/api";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { UserIcon, BotIcon } from "lucide-react";

interface ChatMessageBubbleProps {
    message: ChatMessage;
}

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
    const isUser = message.role === 'user';

    return (
        <div className={cn(
            "flex w-full gap-2 my-2",
            isUser ? "flex-row-reverse" : "flex-row"
        )}>
            <div className={cn(
                "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
                isUser ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
            )}>
                {isUser ? <UserIcon size={16} /> : <BotIcon size={16} />}
            </div>

            <div className={cn(
                "p-3 rounded-2xl max-w-[85%] text-sm shadow-sm",
                isUser
                    ? "bg-primary text-primary-foreground rounded-tr-none"
                    : "bg-muted/50 border border-border/50 rounded-tl-none"
            )}>
                <div className="prose prose-invert prose-sm break-words leading-relaxed">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
}
