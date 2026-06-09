"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function PromptBox() {
  const [prompt, setPrompt] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const sendMessage = () => {
    if (!prompt.trim()) return;

    console.log(prompt);

    setPrompt("");

    if (textareaRef.current) {
      textareaRef.current.style.height = "60px";
    }
  };

  const handleInput = (
    e: React.ChangeEvent<HTMLTextAreaElement>,
  ) => {
    const el = e.target;

    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;

    setPrompt(el.value);
  };

  const handleKeyDown = (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="border-t border-zinc-800 p-4">
      <div className="mx-auto flex max-w-4xl items-center gap-3">
        <Textarea
          ref={textareaRef}
          value={prompt}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          className="
            min-h-[60px]
            max-h-[180px]
            resize-none
            overflow-y-auto
          "
        />

        <Button
          onClick={sendMessage}
          className="shrink-0"
        >
          Send
        </Button>
      </div>
    </div>
  );
}