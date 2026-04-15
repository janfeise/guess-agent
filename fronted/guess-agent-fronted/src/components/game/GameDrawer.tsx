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
import styles from "./GameDrawer.module.css";

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
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 32 }}
            className="fixed inset-y-0 left-0 z-[60] w-full max-w-[min(92vw,30rem)] flex flex-col overflow-hidden border-outline/10 bg-surface/95 shadow-[0_24px_80px_rgba(0,0,0,0.18)] backdrop-blur-xl"
          >
            <div className={styles.drawerHeader}>
              <h2 className={styles.drawerTitle}>词汇情报</h2>
              <button
                type="button"
                onClick={onClose}
                className={styles.closeButton}
                aria-label="关闭抽屉"
              >
                <PanelRightClose className="h-5 w-5" />
              </button>
            </div>

            <div className={styles.drawerContent}>
              <div className={styles.panelWrapper}>
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

              <div className={styles.tabsContainer}>
                <button
                  type="button"
                  onClick={() => onChangeTab("assistant")}
                  className={`${styles.tabButton} ${activeTab === "assistant" ? styles.active : ""}`}
                >
                  <Bot className={styles.tabIcon} />
                  辅助面板
                </button>
                <button
                  type="button"
                  onClick={() => onChangeTab("history")}
                  className={`${styles.tabButton} ${activeTab === "history" ? styles.active : ""}`}
                >
                  <HistoryIcon className={styles.tabIcon} />
                  回合历史
                </button>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
