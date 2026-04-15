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

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hour = String(date.getHours() + 8).padStart(2, "0");
  const minute = String(date.getMinutes()).padStart(2, "0");

  return `${year}/${month}/${day} ${hour}:${minute}`;
}

export default function GameAssistantPanel({
  gameState,
  durationLabel,
}: GameAssistantPanelProps) {
  return (
    <div className="flex h-full min-h-0 flex-col gap-4 overflow-hidden">
      <div className="grid min-h-0 gap-3 overflow-y-auto pb-1">
        <div className="rounded-[1.25rem] bg-white px-5 py-4 h-[100px] w-full overflow-hidden">
          <p className="text-[12px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            用户词
          </p>
          <p className="mt-2 w-full break-words text-3xl font-headline font-bold text-primary">
            {gameState?.currentUserWord || "暂无"}
          </p>
        </div>

        <div className="rounded-[1.25rem] bg-white px-5 py-4 h-[100px] w-full overflow-hidden pb-5">
          <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant/60">
            加密系统词
          </p>
          <p className="mt-2 w-full break-words text-xs font-headline font-bold text-on-surface-variant/30">
            {gameState?.systemWordEncrypted || "暂无"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-[1.5rem] bg-surface-container-low p-4">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
            对局轮次
          </p>
          <p className="mt-2 font-headline text-3xl font-extrabold text-primary">
            <span className="text-2xl">Round</span> {gameState?.roundCount ?? 0}
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

      <div className="rounded-[1.75rem] bg-surface-container-low px-5 py-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
          对局创建时间
        </p>
        <p className="mt-2 font-headline text-base font-bold text-on-surface">
          {formatCreatedAt(gameState?.createdAt)}
        </p>
      </div>
    </div>
  );
}
