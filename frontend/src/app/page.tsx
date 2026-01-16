"use client";

import { ArticleCard } from "@/components/article-card";
import { api } from "@/lib/api";
import { SortField, SortOrder } from "@/types/api";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Loader2Icon, RefreshCcw, Sparkles } from "lucide-react";
import { useEffect } from "react";
import { useInView } from "react-intersection-observer";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/stores/chat";
import { MessageCircleIcon } from "lucide-react";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth";
import { LoginDialog } from "@/components/auth/login-dialog";
import { ModeToggle } from "@/components/mode-toggle";

export default function Home() {
  const { ref, inView } = useInView();
  const { openChat } = useChatStore();
  const authStore = useAuthStore();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
    refetch
  } = useInfiniteQuery({
    queryKey: ["articles"],
    queryFn: ({ pageParam = 1 }) =>
      api.getArticles({ page: pageParam, size: 12, sort_by: SortField.POSTED_AT, order: SortOrder.DESC }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) =>
      lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined,
  });

  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage, hasNextPage]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-black tracking-tighter bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            HN Chinese
          </h1>
          <div className="flex items-center gap-2">
            {!authStore.token ? (
              <>
                <LoginDialog>
                  <Button variant="ghost" size="sm">Login</Button>
                </LoginDialog>
                <Button size="sm" asChild>
                  <Link href="/signup">Sign Up</Link>
                </Button>
              </>
            ) : (
              <Button variant="ghost" size="sm" onClick={() => authStore.logout()}>
                Logout
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              className="gap-2 hidden md:flex cursor-pointer"
              onClick={() => openChat('global')}
            >
              <MessageCircleIcon className="w-4 h-4" />
              Global Chat
            </Button>
            <Button variant="ghost" size="icon" onClick={() => refetch()} disabled={status === 'pending'}>
              <RefreshCcw className={`w-4 h-4 ${status === 'pending' ? 'animate-spin' : ''}`} />
            </Button>
            <ModeToggle />
          </div>
        </div>
      </header>

      <main className="container max-w-4xl mx-auto px-4 py-8">
        {status === "pending" ? (
          <div className="flex flex-col gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 rounded-xl border border-muted bg-muted/20 animate-pulse" />
            ))}
          </div>
        ) : status === "error" ? (
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <p className="mb-4">Failed to load articles</p>
            <Button onClick={() => refetch()}>Try Again</Button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {data.pages.map((page) =>
              page.items.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))
            )}
          </div>
        )}

        {/* Infinite Scroll Trigger */}
        <div ref={ref} className="py-8 flex justify-center w-full">
          {isFetchingNextPage && <Loader2Icon className="w-6 h-6 animate-spin text-muted-foreground" />}
          {!hasNextPage && status === 'success' && (
            <p className="text-sm text-muted-foreground opacity-50">You've reached the end</p>
          )}
        </div>
      </main>
    </div>
  );
}
