import { cn } from "@/src/lib/utils";
import { Sparkles } from "lucide-react";

interface ChatBubbleProps {
  role: "ai" | "user";
  content: string;
  name?: string;
}

export default function ChatBubble({ role, content, name }: ChatBubbleProps) {
  const isAi = role === "ai";

  return (
    <div
      className={cn(
        "flex flex-col gap-2 max-w-[85%]",
        isAi ? "self-start" : "self-end items-end",
      )}
    >
      <div className="flex items-center gap-2 mb-1 px-1">
        {isAi && <Sparkles className="w-3 h-3 text-tertiary" />}
        <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">
          {name || (isAi ? "空灵向导" : "你")}
        </span>
      </div>
      <div
        className={cn(
          "p-5 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.02)]",
          isAi
            ? "bg-tertiary-container text-white  rounded-bl-none font-headline font-medium text-lg leading-relaxed"
            : "bg-white text-on-surface rounded-br-none text-base",
        )}
      >
        <p>{content}</p>
      </div>
    </div>
  );
}
