import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ChatPanel } from "@/components/chat/chat-panel";
import { LayoutShifter } from "@/components/layout-shifter";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Hacker News Chinese",
  description: "AI-powered Hacker News aggregator with Chinese summaries.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        <Providers>
          <LayoutShifter>
            {children}
          </LayoutShifter>
          <div className="fixed z-[100]">
            <ChatPanel />
          </div>
        </Providers>
      </body>
    </html>
  );
}
