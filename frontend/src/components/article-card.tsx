"use client";

import { ArticleSchema } from "@/types/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CalendarIcon, MessageSquareIcon, ExternalLinkIcon, StarIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useChatStore } from "@/stores/chat";

interface ArticleCardProps {
    article: ArticleSchema;
}

export function ArticleCard({ article }: ArticleCardProps) {
    const { openChat } = useChatStore();
    const formattedDate = new Date(article.posted_at).toLocaleDateString("zh-CN", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });

    return (
        <Card className="flex flex-col h-full transition-all duration-300 hover:border-primary/50 hover:shadow-lg border-muted">
            <CardHeader className="pb-3">
                <div className="flex justify-between items-start gap-4">
                    <CardTitle className="text-lg font-bold leading-tight tracking-tight">
                        <a
                            href={article.original_url || "#"}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-primary transition-colors flex items-center gap-2"
                        >
                            {article.detailed_analysis?.title_cn || article.original_title}
                            <ExternalLinkIcon className="w-4 h-4 opacity-50" />
                        </a>
                    </CardTitle>
                    <Badge variant="secondary" className="shrink-0 flex gap-1 items-center">
                        <StarIcon className="w-3 h-3 text-yellow-500" />
                        {article.score}
                    </Badge>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mt-2">
                    <span className="flex items-center gap-1">
                        <CalendarIcon className="w-3 h-3" />
                        {formattedDate}
                    </span>
                    <span>by {article.by}</span>
                    {article.detailed_analysis && (
                        <Badge variant="outline" className="text-[10px] py-0 h-5 border-blue-500/30 text-blue-400">
                            AI Score: {article.detailed_analysis.ai_score}
                        </Badge>
                    )}
                </div>
            </CardHeader>
            <CardContent className="flex-grow text-sm text-muted-foreground">
                {article.detailed_analysis?.summary ? (
                    <div className="prose prose-invert prose-sm max-w-none line-clamp-4">
                        <ReactMarkdown>{article.detailed_analysis.summary}</ReactMarkdown>
                    </div>
                ) : (
                    <p className="line-clamp-4 italic opacity-60">
                        Scanning content...
                    </p>
                )}
            </CardContent>
            <CardFooter className="pt-2 border-t border-border/40 flex justify-between">
                <div className="flex gap-2">
                    {article.detailed_analysis?.tech_stack?.slice(0, 3).map((tech) => (
                        <Badge key={tech} variant="outline" className="text-xs font-normal opacity-70">
                            {tech}
                        </Badge>
                    ))}
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    className="gap-2 text-primary hover:text-primary hover:bg-primary/10"
                    onClick={() => openChat('article', article.id, article.original_title)}
                >
                    <MessageSquareIcon className="w-4 h-4" />
                    Chat
                </Button>
            </CardFooter>
        </Card>
    );
}
