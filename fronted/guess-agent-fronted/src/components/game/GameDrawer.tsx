import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  ChevronRight,
  PanelRightClose,
  Bot,
  History as HistoryIcon,
} from "lucide-react";
import GameAssistantPanel from "./GameAssistantPanel";
import GameHistoryPanel from "./GameHistoryPanel";
import { GameState } from "@/src/types/game";

export type GameDrawerTab = "assistant" | "history";

interface GameDrawerProps {
  isOpen: boolean;
  activeTab: GameDrawerTab;
  onClose: () => void;
  onChangeTab: (tab: GameDrawerTab) => void;
  gameState: GameState | null;
}

function formatDuration(ms: number) {
  const safeMs = Math.max(0, ms);
  const totalSeconds = Math.floor(safeMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;

  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

export default function GameDrawer({
  isOpen,
  activeTab,
  onClose,
  onChangeTab,
  gameState,
}: GameDrawerProps) {
  const [selectedRoundNo, setSelectedRoundNo] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  const sortedHistory = useMemo(
    () =>
      [...(gameState?.history ?? [])].sort(
        (left, right) => right.round_no - left.round_no,
      ),
    [gameState?.history],
  );

  const durationLabel = useMemo(() => {
    if (!gameState?.startTime) {
      return "0:00";
    }

    return formatDuration(now - gameState.startTime);
  }, [gameState?.startTime, now]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const timer = window.setInterval(() => {
      setNow(Date.now());
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen || activeTab !== "history" || sortedHistory.length === 0) {
      return;
    }

    setSelectedRoundNo((current) => {
      if (
        current != null &&
        sortedHistory.some((item) => item.round_no === current)
      ) {
        return current;
      }

      return sortedHistory[0].round_no;
    });
  }, [isOpen, activeTab, sortedHistory]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 z-[55] bg-on-surface/25 backdrop-blur-[2px]"
            onClick={onClose}
          />

          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 32 }}
            className="fixed inset-y-0 right-0 z-[60] flex h-full w-full max-w-[min(92vw,30rem)] flex-col overflow-hidden border-l border-outline/10 bg-surface/95 shadow-[0_24px_80px_rgba(0,0,0,0.18)] backdrop-blur-xl"
          >
            <div className="flex items-start justify-between gap-4 bg-gradient-to-b from-primary/12 via-surface to-surface px-6 py-5">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.35em] text-on-surface-variant/60">
                  对局抽屉
                </p>
                <h2 className="mt-2 font-headline text-2xl font-extrabold text-primary">
                  辅助面板与回合历史
                </h2>
              </div>

              <button
                type="button"
                onClick={onClose}
                className="flex h-11 w-11 items-center justify-center rounded-2xl bg-surface-container-low text-on-surface-variant transition-transform duration-200 active:scale-95"
                aria-label="关闭抽屉"
              >
                <PanelRightClose className="h-5 w-5" />
              </button>
            </div>

            <div className="px-6 pb-4">
              <div className="grid grid-cols-2 rounded-[1.5rem] bg-surface-container-low p-1">
                <button
                  type="button"
                  onClick={() => onChangeTab("assistant")}
                  className={`flex items-center justify-center gap-2 rounded-[1.25rem] px-4 py-3 text-sm font-bold transition-all duration-200 ${
                    activeTab === "assistant"
                      ? "bg-primary text-on-primary shadow-[0_10px_22px_rgba(0,108,90,0.22)]"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  <Bot className="h-4 w-4" />
                  辅助面板
                </button>
                <button
                  type="button"
                  onClick={() => onChangeTab("history")}
                  className={`flex items-center justify-center gap-2 rounded-[1.25rem] px-4 py-3 text-sm font-bold transition-all duration-200 ${
                    activeTab === "history"
                      ? "bg-primary text-on-primary shadow-[0_10px_22px_rgba(0,108,90,0.22)]"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  <HistoryIcon className="h-4 w-4" />
                  回合历史
                </button>
              </div>
            </div>

            <div className="flex-1 min-h-0 overflow-hidden px-6 pb-6">
              <AnimatePresence mode="wait" initial={false}>
                {activeTab === "assistant" ? (
                  <motion.div
                    key="assistant-panel"
                    initial={{ opacity: 0, x: 16 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -16 }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className="h-full"
                  >
                    <GameAssistantPanel
                      gameState={gameState}
                      durationLabel={durationLabel}
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    key="history-panel"
                    initial={{ opacity: 0, x: 16 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -16 }}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                    className="h-full"
                  >
                    <GameHistoryPanel
                      history={sortedHistory}
                      selectedRoundNo={selectedRoundNo}
                      onSelectRound={setSelectedRoundNo}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
