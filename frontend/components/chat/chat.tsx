"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import { Send, Paperclip } from "lucide-react";

type Message = {
    role: "user" | "assistant";
    content: string;
};

function seededRandom(seed: number) {
    let x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
}

export function Chat() {
    const [input, setInput] = useState("");

    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content:
                "Welcome back, Suyash. What would you like to learn today?",
        },
    ]);

    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const messagesRef = useRef<HTMLDivElement>(null);

    /* ---------------- Smooth textarea resize (no layout thrash) ---------------- */
    useEffect(() => {
        const el = textareaRef.current;
        if (!el) return;

        const id = requestAnimationFrame(() => {
            el.style.height = "auto";

            const nextHeight = el.scrollHeight;
            const maxHeight = 160;

            el.style.height =
                Math.min(nextHeight, maxHeight) + "px";

            el.style.overflowY =
                nextHeight > maxHeight ? "auto" : "hidden";
        });

        return () => cancelAnimationFrame(id);
    }, [input]);

    const sendMessage = () => {
        if (!input.trim()) return;

        setMessages((prev) => [
            ...prev,
            { role: "user", content: input },
        ]);

        setInput("");

        requestAnimationFrame(() => {
            const el = textareaRef.current;
            if (!el) return;

            el.style.height = "60px";
            el.style.overflowY = "hidden";
        });
    };

    /* ---------------- Stable scroll (only on count change) ---------------- */
    useEffect(() => {
        const el = messagesRef.current;
        if (!el) return;

        const id = requestAnimationFrame(() => {
            el.scrollTop = el.scrollHeight;
        });

        return () => cancelAnimationFrame(id);
    }, [messages.length]);

    /* ---------------- Precompute message visuals (avoid recompute spam) ---------------- */
    const renderedMessages = useMemo(() => {
        return messages.map((message, index) => {
            const seed =
                message.role === "assistant"
                    ? index * 1337
                    : index * 9999;

            const jitterX =
                seededRandom(seed + 1) * 6 - 3;
            const jitterY =
                seededRandom(seed + 2) * 6 - 3;
            const opacity =
                0.6 + seededRandom(seed + 3) * 0.4;

            return {
                ...message,
                jitterX,
                jitterY,
                opacity,
            };
        });
    }, [messages]);

    return (
        <div className="flex h-full flex-col bg-[#05070d] text-white">
            {/* Messages */}
            <div ref={messagesRef} className="flex-1 overflow-y-auto">
                {messages.length === 0 ? (
                    <div className="flex h-full items-center justify-center px-8">
                        <div className="max-w-3xl text-center">
                            <h1 className="text-6xl font-black leading-[0.95] tracking-tight">
                                What would you like
                                <br />
                                <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-500 bg-clip-text text-transparent">
                                    to learn today?
                                </span>
                            </h1>

                            <p className="mt-6 text-lg text-zinc-400">
                                Ask anything about computer science,
                                mathematics, networking, systems,
                                engineering, or programming.
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="mx-auto max-w-4xl px-8 py-12">
                        <div className="space-y-12">
                            {renderedMessages.map((message, index) => (
                                <div
                                    key={index}
                                    className="max-w-full"
                                    style={{
                                        transform: `translate(${message.jitterX}px, ${message.jitterY}px)`,
                                        opacity: message.opacity,
                                    }}
                                >
                                    <div
                                        className={`mb-3 text-xs font-medium uppercase tracking-[0.2em] ${
                                            message.role === "assistant"
                                                ? "text-violet-400"
                                                : "text-zinc-500"
                                        }`}
                                    >
                                        {message.role === "assistant"
                                            ? "Recursive"
                                            : "You"}
                                    </div>

                                    <div className="text-lg leading-8 text-zinc-200">
                                        {message.content}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="shrink-0 px-8 pb-8 pt-4">
                <div className="mx-auto max-w-5xl">
                    <div className="rounded-3xl border border-white/10 bg-[#0f1320] shadow-2xl shadow-black/20">
                        <div className="p-5">
                            <textarea
                                ref={textareaRef}
                                rows={2}
                                value={input}
                                onChange={(e) =>
                                    setInput(e.target.value)
                                }
                                onKeyDown={(e) => {
                                    if (
                                        e.key === "Enter" &&
                                        !e.shiftKey &&
                                        !e.nativeEvent.isComposing
                                    ) {
                                        e.preventDefault();
                                        sendMessage();
                                    }
                                }}
                                placeholder="Ask Recursive anything..."
                                className="
                                    block
                                    w-full
                                    resize-none
                                    overflow-y-hidden
                                    bg-transparent
                                    text-base
                                    leading-7
                                    text-white
                                    outline-none
                                    placeholder:text-zinc-500
                                "
                            />
                        </div>

                        <div className="flex items-center justify-between border-t border-white/5 px-4 py-3">
                            <button className="rounded-xl p-2 text-zinc-400 transition hover:bg-white/5 hover:text-white">
                                <Paperclip size={18} />
                            </button>

                            <button
                                onClick={sendMessage}
                                className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium transition hover:bg-violet-500"
                            >
                                <Send size={16} />
                                Send
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}