"use client";

import { useQueryClient, useMutation } from "@tanstack/react-query";
import { ArticleSchema, ArticleListResponse } from "@/types/api";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeftIcon, CalendarIcon, ExternalLinkIcon, MessageSquareIcon, StarIcon, HeartIcon, ThumbsUpIcon, BookmarkIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useChatStore } from "@/stores/chat";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/lib/api";
import { ModeToggle } from "@/components/mode-toggle";

export default function ArticleDetailPage() {
    const params = useParams();
    const router = useRouter();
    const id = Number(params.id);
    const queryClient = useQueryClient();
    const { openChat } = useChatStore();
    const token = useAuthStore((state) => state.token);

    const [article, setArticle] = useState<ArticleSchema | null>(null);

    // Initial state setup from article when available
    const [isFavorited, setIsFavorited] = useState(false);
    const [favoritesCount, setFavoritesCount] = useState(0);
    const [isReadLater, setIsReadLater] = useState(false);

    useEffect(() => {
        if (article) {
            setIsFavorited(article.is_favorited || false);
            setFavoritesCount(article.favorites_count || 0);
            setIsReadLater(article.is_read_later || false);
        }
    }, [article]);

    const toggleFavoriteMutation = useMutation({
        mutationFn: async () => {
            if (!token) throw new Error("Please sign in to favorite");
            if (!article) return;
            if (isFavorited) {
                await api.removeFavorite(article.id, token);
            } else {
                await api.addFavorite(article.id, token);
            }
        },
        onMutate: async () => {
            const previousIsFavorited = isFavorited;
            const previousCount = favoritesCount;
            setIsFavorited(!previousIsFavorited);
            setFavoritesCount(prev => previousIsFavorited ? prev - 1 : prev + 1);
            return { previousIsFavorited, previousCount };
        },
        onError: (err, variables, context) => {
            if (context) {
                setIsFavorited(context.previousIsFavorited);
                setFavoritesCount(context.previousCount);
            }
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
            if (!article) return;
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

    useEffect(() => {
        if (!id) return;
        // ... cache logic unchanged ...
        const queries = queryClient.getQueryCache().findAll({ queryKey: ["articles"] });
        let foundArticle: ArticleSchema | undefined;
        for (const query of queries) {
            const data = query.state.data as any;
            if (data?.pages) {
                for (const page of data.pages) {
                    const found = (page as ArticleListResponse).items.find(item => item.id === id);
                    if (found) { foundArticle = found; break; }
                }
            } else if (data?.items) {
                foundArticle = (data as ArticleListResponse).items.find(item => item.id === id);
            }
            if (foundArticle) break;
        }
        if (foundArticle) { setArticle(foundArticle); }
    }, [id, queryClient]);

    if (!article) {
        // ... not found logic unchanged ...
        return (
            <div className="container max-w-4xl mx-auto px-4 py-20 flex flex-col items-center justify-center text-center gap-4">
                <h1 className="text-2xl font-bold">Article not found in cache</h1>
                <p className="text-muted-foreground">Since we don't have a direct backend endpoint for IDs yet, please go back to the list to load data.</p>
                <Button onClick={() => router.push("/")}>
                    <ArrowLeftIcon className="w-4 h-4 mr-2" />
                    Back to Home
                </Button>
            </div>
        )
    }

    const formattedDate = new Date(article.posted_at).toLocaleDateString("zh-CN", {
        month: "long",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });

    return (
        <div className="min-h-screen bg-background text-foreground pb-20 overflow-x-hidden">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="w-full lg:w-3/5 mx-auto px-4 h-16 flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeftIcon className="w-5 h-5" />
                    </Button>
                    <h1 className="text-lg font-bold truncate flex-1">
                        {article.detailed_analysis?.title_cn || article.original_title}
                    </h1>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-9 w-9 ${isFavorited ? 'text-red-500 hover:text-red-600' : 'text-muted-foreground hover:text-red-500'}`}
                            onClick={(e) => {
                                e.preventDefault();
                                toggleFavoriteMutation.mutate();
                            }}
                        >
                            <HeartIcon className={`w-5 h-5 ${isFavorited ? 'fill-current' : ''}`} />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            className={`h-9 w-9 ${isReadLater ? 'text-primary hover:text-primary' : 'text-muted-foreground hover:text-primary'}`}
                            onClick={(e) => {
                                e.preventDefault();
                                toggleReadLaterMutation.mutate();
                            }}
                        >
                            <BookmarkIcon className={`w-5 h-5 ${isReadLater ? 'fill-current' : ''}`} />
                        </Button>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openChat('article', article.id, article.original_title)}
                        className="ml-2"
                    >
                        <MessageSquareIcon className="w-4 h-4 mr-2" />
                        Chat
                    </Button>
                </div>
                <div className="flex items-center gap-2">
                    <ModeToggle />
                </div>
            </header>

            <main className="w-full lg:w-3/5 mx-auto px-4 py-8 space-y-8">

                {/* Header Section */}
                <section className="space-y-4">
                    <div className="flex flex-wrap gap-2 items-center">
                        <Badge variant="outline" className="text-muted-foreground border-muted-foreground/30">
                            HN Score: {article.score}
                        </Badge>
                        {article.detailed_analysis && (
                            <Badge variant="outline" className="text-blue-400 border-blue-500/30">
                                AI Score: {article.detailed_analysis.ai_score}
                            </Badge>
                        )}
                        {favoritesCount > 0 && (
                            <Badge variant="secondary" className="text-red-500 bg-red-400/10 hover:bg-red-400/20">
                                <HeartIcon className="w-3 h-3 mr-1" />
                                {favoritesCount}
                            </Badge>
                        )}
                        <span className="flex items-center text-sm text-muted-foreground ml-auto">
                            <CalendarIcon className="w-3 h-3 mr-1" />
                            {formattedDate}
                        </span>
                    </div>

                    <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight lg:text-5xl leading-tight">
                        {article.detailed_analysis?.title_cn || article.original_title}
                    </h1>

                    <a
                        href={article.original_url || "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline flex items-center gap-1 text-sm font-medium"
                    >
                        {article.original_title}
                        <ExternalLinkIcon className="w-3 h-3" />
                    </a>

                    <div className="flex flex-wrap gap-2 pt-2">
                        {article.detailed_analysis?.tech_stack?.map((tech) => (
                            <Badge key={tech} variant="outline" className="text-sm py-1 px-3">
                                {tech}
                            </Badge>
                        ))}
                    </div>
                </section>

                <hr className="border-border/40" />

                {/* Content Section */}
                {article.detailed_analysis ? (
                    <div className="space-y-8">
                        <section className="prose prose-invert prose-lg max-w-none">
                            <h3 className="text-xl font-semibold mb-4 text-primary">AI Summary</h3>
                            <div className="bg-muted/30 p-6 rounded-2xl border border-border/50">
                                <ReactMarkdown>{article.detailed_analysis.summary}</ReactMarkdown>
                            </div>
                        </section>

                        <section>
                            <h3 className="text-xl font-semibold mb-4 text-primary">Key Points</h3>
                            <ul className="grid gap-3">
                                {article.detailed_analysis.key_points.map((point, idx) => (
                                    <li key={idx} className="flex gap-3 items-start bg-card p-4 rounded-xl border border-muted shadow-sm">
                                        <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold mt-0.5">
                                            {idx + 1}
                                        </span>
                                        <span className="text-muted-foreground leading-relaxed">{point}</span>
                                    </li>
                                ))}
                            </ul>
                        </section>

                        <section>
                            <h3 className="text-xl font-semibold mb-4 text-primary">Takeaway</h3>
                            <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 p-6 rounded-2xl border border-indigo-500/20">
                                <p className="text-lg italic font-medium leading-relaxed">
                                    "{article.detailed_analysis.takeaway}"
                                </p>
                            </div>
                        </section>

                        {/* Full Translated Content */}
                        {article.detailed_analysis.url_content_trans && (
                            <section className="prose prose-invert prose-lg max-w-none pt-4">
                                <hr className="border-border/40 mb-8" />
                                <h3 className="text-xl font-semibold mb-6 text-primary flex items-center gap-2">
                                    <span className="bg-primary/20 w-8 h-8 rounded-lg flex items-center justify-center text-sm">文</span>
                                    Full Translated Content
                                </h3>
                                <div className="bg-muted/10 p-6 md:p-8 rounded-3xl border border-border/30">
                                    <ReactMarkdown
                                        components={{
                                            h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-4 mt-6 text-foreground" {...props} />,
                                            h2: ({ node, ...props }) => <h2 className="text-xl font-bold mb-3 mt-5 text-foreground" {...props} />,
                                            h3: ({ node, ...props }) => <h3 className="text-lg font-bold mb-2 mt-4 text-foreground/90" {...props} />,
                                            p: ({ node, ...props }) => <p className="leading-relaxed mb-4 text-muted-foreground" {...props} />,
                                            ul: ({ node, ...props }) => <ul className="list-disc pl-6 mb-4 space-y-2" {...props} />,
                                            ol: ({ node, ...props }) => <ol className="list-decimal pl-6 mb-4 space-y-2" {...props} />,
                                            li: ({ node, ...props }) => <li className="text-muted-foreground" {...props} />,
                                            code: ({ node, ...props }) => <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-primary" {...props} />,
                                            blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-primary/30 pl-4 italic text-muted-foreground my-4" {...props} />,
                                        }}
                                    >
                                        {article.detailed_analysis.url_content_trans}
                                    </ReactMarkdown>
                                </div>
                            </section>
                        )}
                    </div>
                ) : (
                    <div className="py-20 text-center text-muted-foreground">
                        Processing content...
                    </div>
                )}
            </main>
        </div>
    );
}
