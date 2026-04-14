import { Bot, Sparkles } from "lucide-react";
import { GameState } from "@/src/types/game";

interface GameAssistantPanelProps {
  gameState: GameState | null;
  durationLabel: string;
}

function formatDifficulty(difficulty?: string) {
  switch (difficulty) {
    case "easy":
      return "简单";
    case "medium":
      return "中等";
    case "hard":
      return "困难";
    default:
      return difficulty || "中等";
  }
}

function formatStatus(status?: string) {
  switch (status) {
    case "active":
      return "进行中";
    case "finished_win":
      return "已获胜";
    case "finished_loss":
      return "已结束";
    default:
      return "未知";
  }
}

function formatCreatedAt(createdAt?: string) {
  if (!createdAt) return "暂无";

  const date = new Date(createdAt);
  if (Number.isNaN(date.getTime())) return createdAt;

  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function GameAssistantPanel({
  gameState,
  durationLabel,
}: GameAssistantPanelProps) {
  return (
    <div className="flex h-full min-h-0 flex-col gap-4 overflow-hidden">
      <div className="rounded-[2rem] bg-gradient-to-br from-primary to-primary-dim px-5 py-5 text-on-primary shadow-[0_18px_40px_rgba(0,108,90,0.22)]">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/15 backdrop-blur-sm">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.35em] text-white/70">
              辅助面板
            </p>
            <h3 className="mt-1 font-headline text-xl font-extrabold">
              对局概览
            </h3>
          </div>
        </div>
        <p className="mt-4 text-sm leading-relaxed text-white/80">
          系统词已加密隐藏，仅展示当前对局的公开信息与关键状态。
        </p>
        <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-white/80">
          <Sparkles className="h-3.5 w-3.5" />
          主题色统一视觉
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-[1.5rem] bg-surface-container-low p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            对局轮次
          </p>
          <p className="mt-2 font-headline text-3xl font-extrabold text-primary">
            {gameState?.roundCount ?? 0}
          </p>
        </div>
        <div className="rounded-[1.5rem] bg-surface-container-low p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            难度
          </p>
          <p className="mt-2 font-headline text-2xl font-extrabold text-on-surface">
            {formatDifficulty(gameState?.difficulty)}
          </p>
        </div>
        <div className="rounded-[1.5rem] bg-surface-container-low p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            对局时间
          </p>
          <p className="mt-2 font-headline text-2xl font-extrabold text-on-surface">
            {durationLabel}
          </p>
        </div>
        <div className="rounded-[1.5rem] bg-surface-container-low p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            状态
          </p>
          <p className="mt-2 font-headline text-2xl font-extrabold text-primary">
            {formatStatus(gameState?.status)}
          </p>
        </div>
      </div>

      <div className="grid min-h-0 gap-3 overflow-y-auto pb-1">
        <div className="rounded-[1.75rem] bg-surface-container-low px-5 py-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            用户词
          </p>
          <p className="mt-2 break-words text-lg font-headline font-bold text-primary">
            {gameState?.currentUserWord || "暂无"}
          </p>
        </div>

        <div className="rounded-[1.75rem] bg-surface-container-low px-5 py-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            系统词加密数据
          </p>
          <p className="mt-2 break-all rounded-2xl bg-surface px-4 py-3 text-[12px] leading-relaxed text-on-surface-variant">
            {gameState?.systemWordEncrypted || "暂无"}
          </p>
        </div>

        <div className="rounded-[1.75rem] bg-surface-container-low px-5 py-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            对局创建时间
          </p>
          <p className="mt-2 font-headline text-base font-bold text-on-surface">
            {formatCreatedAt(gameState?.createdAt)}
          </p>
        </div>
      </div>
    </div>
  );
}
