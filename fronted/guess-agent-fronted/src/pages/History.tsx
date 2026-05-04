import { ChevronRight, Sparkles } from "lucide-react";
import { motion } from "motion/react";
import { useState, useEffect } from "react";
import { useAnonymousStore } from "@/src/store/useAnonymousStore";
import { gameApiClient } from "@/src/services/gameApiClient";
import { GameDetailsResponse } from "@/src/types/game";
import {
  formatDateTime,
  getGameResultLabel,
  getGameTitle,
  resolveGameOutcome,
} from "@/src/lib/gameRecords";

interface HistoryProps {
  onOpenGame: (gameId: string) => void;
}

export default function History({ onOpenGame }: HistoryProps) {
  const [history, setHistory] = useState<GameDetailsResponse[]>([]);
  const [filter, setFilter] = useState<"all" | "win" | "loss">("all");
  const [isLoading, setIsLoading] = useState(true);
  const { anonymousId, initAnonymousId } = useAnonymousStore();

  // 加载游戏历史数据
  useEffect(() => {
    const loadHistory = async () => {
      try {
        initAnonymousId();
        if (!anonymousId) {
          setHistory([]);
          return;
        }

        const response = await gameApiClient.getUserGameHistory(anonymousId);
        setHistory(response.games);
      } catch (error) {
        console.error("Failed to load history:", error);
        setHistory([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadHistory();
  }, [anonymousId, initAnonymousId]);

  // 过滤历史记录
  const filteredHistory = history.filter((item) => {
    if (filter === "all") return true;
    const outcome = resolveGameOutcome(item);
    if (filter === "win") return outcome === "win";
    if (filter === "loss") return outcome === "loss";
    return true;
  });

  // 计算统计数据
  const stats = {
    total: history.length,
    wins: history.filter((h) => resolveGameOutcome(h) === "win").length,
    winRate:
      history.length > 0
        ? Math.round(
            (history.filter((h) => resolveGameOutcome(h) === "win").length /
              history.length) *
              100,
          )
        : 0,
  };

  return (
    <div className="space-y-10 pb-12 pt-10">
      <section className="pt-8">
        <h2 className="text-4xl font-headline font-extrabold tracking-tight text-on-surface mb-3">
          对局历史
        </h2>
        <p className="text-on-surface-variant max-w-xs text-sm leading-relaxed font-medium">
          记录在直觉档案中，你与灵感向导的精彩旅程。
        </p>
      </section>

      <section className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
        {["全部", "获胜", "落败"].map((label, i) => {
          const filterValue = ["all", "win", "loss"][i] as
            | "all"
            | "win"
            | "loss";
          return (
            <button
              key={label}
              onClick={() => setFilter(filterValue)}
              className={`px-8 py-3 rounded-full text-xs font-bold transition-all whitespace-nowrap ${
                filter === filterValue
                  ? "bg-primary text-white"
                  : "bg-surface-container-high text-on-surface-variant hover:bg-surface-variant"
              }`}
            >
              {label}
            </button>
          );
        })}
      </section>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="inline-flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
            <p className="text-on-surface-variant">加载中...</p>
          </div>
        </div>
      ) : filteredHistory.length > 0 ? (
        <div className="space-y-4">
          {filteredHistory.map((item, i) => (
            <motion.div
              key={item.game_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => onOpenGame(item.game_id)}
              className="group relative bg-white rounded-[2rem] p-6 shadow-[0_8px_32px_rgba(0,0,0,0.03)] transition-all hover:translate-y-[-4px] cursor-pointer"
            >
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-on-surface-variant/50">
                    {formatDateTime(item.updated_at)}
                  </span>
                  <h3 className="text-2xl font-headline font-bold text-on-surface tracking-tight">
                    {getGameTitle(item)}
                  </h3>
                  <div className="flex gap-2 pt-2">
                    <span
                      className={`inline-flex items-center px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                        resolveGameOutcome(item) === "win"
                          ? "bg-primary-container text-on-primary-container"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {getGameResultLabel(item)}
                    </span>
                    <span className="inline-flex items-center px-4 py-1.5 rounded-full bg-surface-container text-on-surface-variant text-[10px] font-bold uppercase tracking-widest">
                      {item.difficulty || "中等"}
                    </span>
                  </div>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-surface-container-low flex items-center justify-center text-primary group-hover:bg-primary-container transition-colors">
                  <ChevronRight className="w-6 h-6" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-on-surface-variant">暂无对局记录</p>
        </div>
      )}

      {history.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="mt-12 p-8 rounded-[2.5rem] bg-surface-container-highest/30 backdrop-blur-md relative overflow-hidden"
        >
          <div className="relative z-10">
            <span className="inline-flex items-center gap-2 text-tertiary font-headline font-bold text-xs mb-4 uppercase tracking-widest">
              <Sparkles className="w-4 h-4" />
              洞察
            </span>
            <h4 className="text-xl font-headline font-bold text-on-surface leading-tight">
              你已完成 {stats.total} 局游戏，赢率为 {stats.winRate}%。
            </h4>
          </div>
          <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-tertiary-container/20 rounded-full blur-3xl" />
        </motion.div>
      )}
    </div>
  );
}
