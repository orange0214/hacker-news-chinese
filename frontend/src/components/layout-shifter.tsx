"use client";

import { useChatStore } from "@/stores/chat";
import { cn } from "@/lib/utils";

export function LayoutShifter({ children }: { children: React.ReactNode }) {
    const { isOpen } = useChatStore();

    return (
        <div
            className={cn(
                "transition-all duration-300 ease-in-out",
                // Only shift on large screens (lg starts at 1024px) where there is enough room
                // Matches ChatPanel width of sm:w-[450px]
                isOpen ? "mr-0 lg:mr-[450px]" : "mr-0"
            )}
        >
            {children}
        </div>
    );
}
