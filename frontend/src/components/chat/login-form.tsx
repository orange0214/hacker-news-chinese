"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { Loader2Icon, LockIcon, MailIcon, UserIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function LoginForm() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const setAuth = useAuthStore((state) => state.setAuth);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            if (isLogin) {
                const res = await api.login(email, password);
                setAuth(res.access_token, res.user);
            } else {
                const res = await api.signup(email, password);
                // Signup returns user and session
                if (res.session) {
                    setAuth(res.session.access_token, res.user);
                } else {
                    // Maybe auto login or prompt
                    setIsLogin(true);
                    setError("Account created! Please sign in.");
                    setIsLoading(false);
                    return;
                }
            }
        } catch (err: any) {
            setError(err.message || "Something went wrong");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-full p-4 space-y-4">
            <Card className="w-full max-w-sm border-0 shadow-none bg-transparent">
                <CardHeader>
                    <div className="flex justify-center mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                            <UserIcon size={24} />
                        </div>
                    </div>
                    <CardTitle className="text-center text-2xl">{isLogin ? "Welcome Back" : "Create Account"}</CardTitle>
                    <CardDescription className="text-center">
                        {isLogin ? "Sign in to access your AI chat history." : "Join to start chatting with AI."}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <div className="relative">
                                <MailIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Email"
                                    type="email"
                                    className="pl-9"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="relative">
                                <LockIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Password"
                                    type="password"
                                    className="pl-9"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {error && <p className="text-xs text-destructive text-center">{error}</p>}

                        <Button className="w-full" disabled={isLoading}>
                            {isLoading && <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />}
                            {isLogin ? "Sign In" : "Sign Up"}
                        </Button>
                    </form>

                    <div className="mt-4 text-center text-sm">
                        <span className="text-muted-foreground">
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                        </span>
                        <button
                            onClick={() => setIsLogin(!isLogin)}
                            className="font-medium text-primary hover:underline focus:outline-none"
                        >
                            {isLogin ? "Sign Up" : "Sign In"}
                        </button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
