import {
  ArrowRight,
  CalendarClock,
  ChevronRight,
  Clock3,
  History,
  X,
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { GameDetailsResponse } from "@/src/types/game";
import {
  buildMessagesFromHistory,
  formatDateTime,
  getGameBannerMessage,
  getGameResultLabel,
  resolveGameOutcome,
} from "@/src/lib/gameRecords";

interface GameDetailModalProps {
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  detail: GameDetailsResponse | null;
  onClose: () => void;
  onOpenGame: (gameId: string) => void;
}

function badgeClass(outcome: ReturnType<typeof resolveGameOutcome>) {
  if (outcome === "win") {
    return "bg-emerald-100 text-emerald-700";
  }

  if (outcome === "loss") {
    return "bg-rose-100 text-rose-700";
  }

  return "bg-surface-container-high text-on-surface-variant";
}

export default function GameDetailModal({
  isOpen,
  isLoading,
  error,
  detail,
  onClose,
  onOpenGame,
}: GameDetailModalProps) {
  const outcome = detail ? resolveGameOutcome(detail) : "active";
  const canContinue = detail?.status === "active";
  const previewHistory = detail
    ? buildMessagesFromHistory(detail.history).slice(-4)
    : [];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[80] bg-black/35 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.section
            initial={{ opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 18, scale: 0.98 }}
            transition={{ type: "spring", stiffness: 260, damping: 26 }}
            className="fixed inset-x-4 top-[10vh] z-[90] mx-auto flex max-h-[80vh] w-[min(100%-2rem,42rem)] flex-col overflow-hidden rounded-[2rem] bg-surface shadow-[0_24px_80px_rgba(0,0,0,0.18)]"
          >
            <header className="flex items-start justify-between gap-4 border-b border-outline/10 px-6 py-5">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full bg-primary-container px-3 py-1 text-[10px] font-bold uppercase tracking-[0.22em] text-primary">
                  <History className="h-3.5 w-3.5" />
                  对局详情
                </div>
                <h3 className="mt-3 text-2xl font-headline font-extrabold text-on-surface">
                  {detail
                    ? detail.user_word || `对局 ${detail.game_id.slice(0, 8)}`
                    : "加载中"}
                </h3>
                <p className="mt-1 text-sm text-on-surface-variant">
                  {detail
                    ? getGameBannerMessage(detail)
                    : "正在读取对局信息..."}
                </p>
              </div>

              <button
                type="button"
                onClick={onClose}
                className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-surface-container-low text-on-surface-variant transition-colors hover:bg-surface-container-high"
                aria-label="关闭详情"
              >
                <X className="h-5 w-5" />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto px-6 py-5">
              {isLoading ? (
                <div className="flex min-h-[24rem] items-center justify-center text-sm text-on-surface-variant">
                  加载中...
                </div>
              ) : error ? (
                <div className="rounded-[1.5rem] bg-rose-50 px-5 py-4 text-rose-700">
                  {error}
                </div>
              ) : detail ? (
                <div className="space-y-5">
                  <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                    <div className="rounded-[1.25rem] bg-surface-container-low px-4 py-4">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
                        状态
                      </p>
                      <p
                        className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-bold ${badgeClass(outcome)}`}
                      >
                        {getGameResultLabel(detail)}
                      </p>
                    </div>
                    <div className="rounded-[1.25rem] bg-surface-container-low px-4 py-4">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
                        轮次
                      </p>
                      <p className="mt-2 text-2xl font-headline font-extrabold text-on-surface">
                        {detail.round_count}
                      </p>
                    </div>
                    <div className="rounded-[1.25rem] bg-surface-container-low px-4 py-4">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
                        难度
                      </p>
                      <p className="mt-2 text-2xl font-headline font-extrabold text-on-surface">
                        {detail.difficulty || "中等"}
                      </p>
                    </div>
                    <div className="rounded-[1.25rem] bg-surface-container-low px-4 py-4">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
                        创建时间
                      </p>
                      <p className="mt-2 text-sm font-semibold text-on-surface">
                        {formatDateTime(detail.created_at)}
                      </p>
                    </div>
                  </div>

                  <div className="rounded-[1.5rem] bg-surface-container-highest/40 px-5 py-4">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/60">
                      当前状态
                    </p>
                    <p className="mt-2 text-base font-medium text-on-surface leading-relaxed">
                      {getGameBannerMessage(detail)}
                    </p>
                    {detail.status === "finished" && (
                      <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-surface-container-low px-4 py-2 text-xs font-bold text-on-surface-variant">
                        <Clock3 className="h-4 w-4" />
                        游戏已结束
                      </div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-on-surface-variant/60">
                        最近对话
                      </h4>
                      <span className="text-xs text-on-surface-variant">
                        仅展示最近 4 条
                      </span>
                    </div>

                    <div className="space-y-3">
                      {previewHistory.length > 0 ? (
                        previewHistory.map((message, index) => (
                          <div
                            key={`${message.role}-${index}`}
                            className="rounded-[1.25rem] border border-outline/10 bg-white px-4 py-4 shadow-[0_4px_20px_rgba(0,0,0,0.03)]"
                          >
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/50">
                                {message.role === "user" ? "用户" : "系统"}
                              </span>
                              <ChevronRight className="h-4 w-4 text-primary/40" />
                            </div>
                            <p className="mt-2 text-sm font-medium leading-relaxed text-on-surface">
                              {message.content}
                            </p>
                          </div>
                        ))
                      ) : (
                        <div className="rounded-[1.25rem] bg-surface-container-low px-4 py-4 text-sm text-on-surface-variant">
                          暂无可展示的对话内容。
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            <footer className="border-t border-outline/10 px-6 py-5">
              {canContinue ? (
                <button
                  type="button"
                  onClick={() => detail && onOpenGame(detail.game_id)}
                  className="flex w-full items-center justify-center gap-2 rounded-[1.25rem] bg-primary px-5 py-4 text-sm font-bold text-white shadow-[0_12px_32px_rgba(0,108,90,0.22)] transition-transform hover:translate-y-[-1px]"
                >
                  进入对局继续
                  <ArrowRight className="h-4 w-4" />
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-3 rounded-[1.25rem] bg-surface-container-low px-4 py-4 opacity-60">
                    <div className="h-11 flex-1 rounded-2xl bg-surface-container" />
                    <div className="h-11 w-14 rounded-2xl bg-surface-container" />
                  </div>
                  <p className="text-xs text-on-surface-variant">
                    游戏已结束，消息发送栏已禁用。
                  </p>
                </div>
              )}
            </footer>
          </motion.section>
        </>
      )}
    </AnimatePresence>
  );
}
