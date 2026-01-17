"use client";

import { useAuthStore } from "@/stores/auth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2, LogOut, User, Mail, Calendar } from "lucide-react";
import Link from "next/link";
import { LayoutShifter } from "@/components/layout-shifter";

export default function ProfilePage() {
    const { user, token, logout } = useAuthStore();
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simple client-side protection
        // In a real app, we might also validate the token with the backend
        if (!token) {
            router.push("/");
        } else {
            setIsLoading(false);
        }
    }, [token, router]);

    const handleLogout = () => {
        logout();
        router.push("/");
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!user) return null;

    // Helper to get initials
    const getInitials = (email: string) => {
        return email.substring(0, 2).toUpperCase();
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return "N/A";
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <div className="min-h-screen bg-background">
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2 font-bold text-lg hover:opacity-80 transition-opacity">
                        ← Back to Home
                    </Link>
                </div>
            </header>

            <main className="container max-w-2xl mx-auto px-4 py-12">
                <Card className="border-border/50 shadow-xl bg-card/50 backdrop-blur-sm">
                    <CardHeader className="text-center pb-2">
                        <div className="mx-auto mb-4">
                            <Avatar className="w-24 h-24 border-4 border-primary/10">
                                <AvatarImage src={user.avatar_url} />
                                <AvatarFallback className="text-2xl bg-primary/10 text-primary">
                                    {getInitials(user.email || "User")}
                                </AvatarFallback>
                            </Avatar>
                        </div>
                        <CardTitle className="text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
                            {user.name || "User Profile"}
                        </CardTitle>
                        <CardDescription className="text-base">
                            Manage your account settings and preferences
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6 mt-6">
                        <div className="grid gap-4">
                            <div className="flex items-center p-4 rounded-lg bg-muted/50 border border-border/50">
                                <Mail className="w-5 h-5 text-muted-foreground mr-3" />
                                <div className="flex-1">
                                    <p className="text-sm text-muted-foreground font-medium">Email</p>
                                    <p className="text-sm font-semibold">{user.email}</p>
                                </div>
                            </div>

                            <div className="flex items-center p-4 rounded-lg bg-muted/50 border border-border/50">
                                <User className="w-5 h-5 text-muted-foreground mr-3" />
                                <div className="flex-1">
                                    <p className="text-sm text-muted-foreground font-medium">User ID</p>
                                    <p className="text-sm font-semibold font-mono">{user.id}</p>
                                </div>
                            </div>

                            {user.created_at && (
                                <div className="flex items-center p-4 rounded-lg bg-muted/50 border border-border/50">
                                    <Calendar className="w-5 h-5 text-muted-foreground mr-3" />
                                    <div className="flex-1">
                                        <p className="text-sm text-muted-foreground font-medium">Joined</p>
                                        <p className="text-sm font-semibold">{formatDate(user.created_at)}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="pt-6 border-t border-border/50">
                            <Button
                                variant="destructive"
                                className="w-full sm:w-auto gap-2"
                                onClick={handleLogout}
                            >
                                <LogOut className="w-4 h-4" />
                                Sign Out
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </main>
        </div>
    );
}
