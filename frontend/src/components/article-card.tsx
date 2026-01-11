"use client";

import { useState } from "react";
import { ArticleSchema } from "@/types/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CalendarIcon, MessageSquareIcon, ExternalLinkIcon, ThumbsUpIcon, HeartIcon, BookmarkIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useChatStore } from "@/stores/chat";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

interface ArticleCardProps {
    article: ArticleSchema;
}

export function ArticleCard({ article }: ArticleCardProps) {
    const { openChat } = useChatStore();
    const token = useAuthStore((state) => state.token);
    const queryClient = useQueryClient();

    // Local state for optimistic updates
    const [isFavorited, setIsFavorited] = useState(article.is_favorited);
    const [favoritesCount, setFavoritesCount] = useState(article.favorites_count || 0);
    const [isReadLater, setIsReadLater] = useState(article.is_read_later);

    const toggleFavoriteMutation = useMutation({
        mutationFn: async () => {
            if (!token) throw new Error("Please sign in to favorite");
            if (isFavorited) {
                await api.removeFavorite(article.id, token);
            } else {
                await api.addFavorite(article.id, token);
            }
        },
        onMutate: async () => {
            // Optimistic update
            const previousIsFavorited = isFavorited;
            const previousCount = favoritesCount;
            setIsFavorited(!previousIsFavorited);
            setFavoritesCount(prev => previousIsFavorited ? prev - 1 : prev + 1);
            return { previousIsFavorited, previousCount };
        },
        onError: (err, variables, context) => {
            // Rollback
            if (context) {
                setIsFavorited(context.previousIsFavorited);
                setFavoritesCount(context.previousCount);
            }
            // Show error (if we have a toast mechanism, use it. For now, we can rely on console)
            console.error(err);
            alert(err.message);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["articles"] });
        }
    });

    const toggleReadLaterMutation = useMutation({
        mutationFn: async () => {
            if (!token) throw new Error("Please sign in to bookmark");
            if (isReadLater) {
                await api.removeReadLater(article.id, token);
            } else {
                await api.addReadLater(article.id, token);
            }
        },
        onMutate: async () => {
            const previousIsReadLater = isReadLater;
            setIsReadLater(!previousIsReadLater);
            return { previousIsReadLater };
        },
        onError: (err, variables, context) => {
            if (context) setIsReadLater(context.previousIsReadLater);
            console.error(err);
            alert(err.message);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["articles"] });
        }
    });

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
                    <CardTitle className="text-2xl font-bold leading-tight tracking-tight">
                        <div className="flex flex-col gap-2">
                            <Link href={`/articles/${article.id}`} className="hover:text-primary transition-colors cursor-pointer">
                                {article.detailed_analysis?.title_cn || article.original_title}
                            </Link>
                            <a
                                href={article.original_url || "#"}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm font-normal text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1 w-fit"
                            >
                                {article.original_title}
                                <ExternalLinkIcon className="w-3 h-3 opacity-50" />
                            </a>
                        </div>
                    </CardTitle>
                    <div className="flex items-center gap-2 shrink-0">
                        <Badge variant="secondary" className="flex gap-1 items-center px-1.5 h-7">
                            <ThumbsUpIcon className="w-3.5 h-3.5 text-orange-500" />
                            <span className="text-sm font-medium">{article.score}</span>
                        </Badge>

                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-7 w-7 ${isFavorited ? 'text-red-500 hover:text-red-600' : 'text-muted-foreground hover:text-red-500'}`}
                            onClick={() => toggleFavoriteMutation.mutate()}
                        >
                            <HeartIcon className={`w-4 h-4 ${isFavorited ? 'fill-current' : ''}`} />
                            {/* Small count next to heart if needed, but badge is separate now. The badge shows GLOBAL count. */}
                        </Button>
                        {favoritesCount > 0 && (
                            <span className="text-xs text-muted-foreground font-mono">{favoritesCount}</span>
                        )}

                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-7 w-7 ${isReadLater ? 'text-primary hover:text-primary' : 'text-muted-foreground hover:text-primary'}`}
                            onClick={() => toggleReadLaterMutation.mutate()}
                        >
                            <BookmarkIcon className={`w-4 h-4 ${isReadLater ? 'fill-current' : ''}`} />
                        </Button>
                    </div>
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
