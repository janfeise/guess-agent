import { Send, Bot, History as HistoryIcon } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useState, useRef, useEffect } from "react";
import ChatBubble from "@/src/components/ChatBubble";
import { useGame } from "@/src/hooks/useGame";
import GameDrawer, { GameDrawerTab } from "@/src/components/game/GameDrawer";
import { GameEndStats, GameOutcome } from "@/src/types/game";
import { getGameBannerMessage } from "@/src/lib/gameRecords";
import styles from "./Game.module.css";
import { useAnonymousStore } from "../store/useAnonymousStore";

interface GameProps {
  difficulty: string;
  userWord: string;
  gameId?: string | null;
  onGameEnd: (outcome: GameOutcome, stats: GameEndStats) => void;
  setGamePageTitle: (title: string) => void; // 用于设置游戏页面标题
  onBackToHistory?: () => void;
}

export default function Game({
  difficulty,
  userWord,
  gameId,
  onGameEnd,
  setGamePageTitle,
  onBackToHistory,
}: GameProps) {
  const {
    gameState,
    messages,
    isLoading,
    error,
    startGame,
    submitUserInput,
    loadGameDetails,
  } = useGame();

  const [inputVal, setInputVal] = useState("");
  const [gameStarted, setGameStarted] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerTab, setDrawerTab] = useState<GameDrawerTab>("assistant");
  const scrollRef = useRef<HTMLDivElement>(null);
  const resultTimerRef = useRef<number | null>(null);
  const isDetailMode = Boolean(gameId);
  const isGameFinished = gameState != null && gameState.status !== "active";
  const { anonymousId, initAnonymousId } = useAnonymousStore();

  // 映射难度等级
  const mapDifficulty = (diff: string): "easy" | "medium" | "hard" => {
    const diffMap: Record<string, "easy" | "medium" | "hard"> = {
      普通: "easy",
      easy: "easy",
      中等: "medium",
      medium: "medium",
      困难: "hard",
      hard: "hard",
    };
    return diffMap[diff] || "medium";
  };

  // 初始化游戏
  useEffect(() => {
    if (gameId) {
      if (!anonymousId) {
        initAnonymousId();
        return;
      }

      setGameStarted(true);
      loadGameDetails(gameId, anonymousId).catch((loadError) => {
        console.error("Failed to load game details:", loadError);
      });
      return;
    }

    if (!gameStarted && userWord) {
      startGame(userWord, mapDifficulty(difficulty));
      setGameStarted(true);
    }
  }, [
    gameStarted,
    userWord,
    difficulty,
    startGame,
    gameId,
    loadGameDetails,
    anonymousId,
    initAnonymousId,
  ]);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // 游戏结束后切换到结果页
  useEffect(() => {
    if (!gameState || gameState.status === "active" || isDetailMode) {
      return;
    }

    if (resultTimerRef.current) {
      window.clearTimeout(resultTimerRef.current);
    }

    const elapsedTime = gameState.startTime
      ? `${Math.floor((Date.now() - gameState.startTime) / 60000)}:${String(Math.floor(((Date.now() - gameState.startTime) % 60000) / 1000)).padStart(2, "0")}`
      : "0:00";

    const outcome: GameOutcome =
      gameState.status === "finished_win" ? "win" : "loss";

    resultTimerRef.current = window.setTimeout(() => {
      onGameEnd(outcome, {
        rounds: gameState.roundCount,
        time: elapsedTime,
        confidence:
          typeof gameState.history[gameState.history.length - 1]?.confidence ===
          "number"
            ? gameState.history[gameState.history.length - 1]?.confidence
            : undefined,
        message: gameState.finalMessage,
        result: gameState.result,
        revealedWord: gameState.revealedWord,
      });
    }, 1500);

    return () => {
      if (resultTimerRef.current) {
        window.clearTimeout(resultTimerRef.current);
        resultTimerRef.current = null;
      }
    };
  }, [gameState, onGameEnd]);

  const handleSend = async () => {
    if (!inputVal.trim() || isLoading || isGameFinished) return;

    const currentInput = inputVal;
    setInputVal("");

    try {
      await submitUserInput(currentInput);
    } catch (err) {
      console.error("Failed to send message:", err);
      setInputVal(currentInput); // 失败时恢复输入
    }
  };

  // 显示错误信息
  useEffect(() => {
    if (error) {
      console.error("Game error:", error);
      // 可选：显示错误提示 UI
    }
  }, [error]);

  const currentRound = gameState?.roundCount || 0;
  const currentPhase = gameState?.phase || "user_turn";

  // 判断当前是否是用户提问阶段
  const isUserTurn = currentPhase === "user_turn";
  // 判断当前是否等待用户回答系统问题
  const isAwaitingAnswer = currentPhase === "waiting_answer";
  // 判断是否等待用户对系统猜测的判断
  const isAwaitingJudgement = currentPhase === "awaiting_judgement";

  useEffect(() => {
    setGamePageTitle(`Round ${currentRound}`);
  }, [currentRound]);

  const openDrawer = (tab: GameDrawerTab) => {
    setDrawerTab(tab);
    setIsDrawerOpen(true);
  };

  return (
    <div className="flex h-full flex-col overflow-hidden pt-16">
      {isGameFinished && (
        <section className="mx-1 mb-4 rounded-[1.75rem] bg-surface-container-high px-5 py-4 shadow-[0_8px_32px_rgba(0,0,0,0.04)]">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-on-surface-variant/60">
                游戏已结束
              </p>
              <h2 className="mt-2 text-xl font-headline font-extrabold text-on-surface">
                {gameState?.status === "finished_win" ? "你获胜了" : "系统获胜"}
              </h2>
              <p className="mt-2 text-sm text-on-surface-variant">
                {gameState?.finalMessage || "本局已经结算。"}
              </p>
            </div>
            {onBackToHistory && (
              <button
                type="button"
                onClick={onBackToHistory}
                className="rounded-full bg-primary-container px-4 py-2 text-xs font-bold text-primary"
              >
                返回历史
              </button>
            )}
          </div>
        </section>
      )}

      {/* Status Bar */}
      <section className={`px-1 py-4 shrink-0 ${styles.topBar}`}>
        <div className="flex items-center gap-2  px-1 py-1  w-fit">
          <button
            type="button"
            onClick={() => openDrawer("assistant")}
            className={`inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[10px] font-bold uppercase tracking-widest transition-all duration-200 ${
              isDrawerOpen && drawerTab === "assistant"
                ? "bg-primary text-on-primary shadow-[0_8px_20px_rgba(0,108,90,0.18)]"
                : "bg-surface hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <Bot className="h-3.5 w-3.5" />
            辅助面板
          </button>
          <button
            type="button"
            onClick={() => openDrawer("history")}
            className={`inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[10px] font-bold uppercase tracking-widest transition-all duration-200 ${
              isDrawerOpen && drawerTab === "history"
                ? "bg-primary text-on-primary shadow-[0_8px_20px_rgba(0,108,90,0.18)]"
                : "bg-surface hover:bg-surface-container text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <HistoryIcon className="h-3.5 w-3.5" />
            回合历史
          </button>
        </div>
      </section>

      {/* Chat Area */}
      <main
        ref={scrollRef}
        className="flex-1 min-h-0 overflow-y-auto px-1 py-6 space-y-8 scroll-smooth pt-9"
      >
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={
                msg.type === "notification"
                  ? "flex justify-center items-center"
                  : msg.role === "user"
                    ? "flex justify-end"
                    : "flex justify-start"
              }
            >
              {msg.type === "notification" ? (
                // 分割线提示消息
                <div className="w-full flex items-center gap-4 px-6">
                  <div className="flex-1 h-[1px] bg-gradient-to-r from-transparent via-outline-variant/30 to-transparent" />
                  <span className="text-xs font-bold text-on-surface-variant uppercase tracking-widest whitespace-nowrap px-2 py-1 bg-surface-container-low rounded-full">
                    {msg.content}
                  </span>
                  <div className="flex-1 h-[1px] bg-gradient-to-r from-transparent via-outline-variant/30 to-transparent" />
                </div>
              ) : (
                <ChatBubble
                  role={msg.role as "ai" | "user"}
                  content={msg.content}
                />
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-start"
          >
            <div className="bg-surface-container-low rounded-3xl px-6 py-4 flex items-center gap-3">
              <div className="flex gap-1">
                <div
                  className="w-2 h-2 rounded-full bg-primary animate-bounce"
                  style={{ animationDelay: "0s" }}
                />
                <div
                  className="w-2 h-2 rounded-full bg-primary animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
                <div
                  className="w-2 h-2 rounded-full bg-primary animate-bounce"
                  style={{ animationDelay: "0.4s" }}
                />
              </div>
              <span className="text-sm text-on-surface-variant">
                AI 正在思考...
              </span>
            </div>
          </motion.div>
        )}
      </main>

      {/* Input Area */}
      <footer className="pt-4 pb-2 shrink-0">
        {error && (
          <div className="mb-3 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 relative">
            <input
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSend()}
              disabled={isLoading || isGameFinished}
              className="w-full bg-surface-container-low border-none rounded-2xl py-5 px-6 focus:ring-2 focus:ring-primary/10 focus:bg-white transition-all text-base placeholder:text-on-surface-variant/40 disabled:opacity-50"
              placeholder={
                isGameFinished
                  ? "游戏已结束，无法继续发送"
                  : isLoading
                    ? "处理中..."
                    : isUserTurn
                      ? "提出你的问题（只能提是/不是问题）..."
                      : isAwaitingAnswer
                        ? "回答 AI 的问题（是/不是）..."
                        : isAwaitingJudgement
                          ? "判断 AI 的猜测..."
                          : "游戏进行中..."
              }
              type="text"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={isLoading || isGameFinished || !inputVal.trim()}
            className="btn-primary-gradient h-14 w-14 rounded-2xl flex items-center justify-center disabled:opacity-50"
          >
            <Send className="h-6 w-6" />
          </button>
        </div>
        {isGameFinished && (
          <p className="px-1 text-xs font-medium text-on-surface-variant/70">
            消息发送栏已禁用，当前页面仅用于查看历史对局。
          </p>
        )}
      </footer>

      <GameDrawer
        isOpen={isDrawerOpen}
        activeTab={drawerTab}
        onClose={() => setIsDrawerOpen(false)}
        onChangeTab={setDrawerTab}
        gameState={gameState}
      />
    </div>
  );
}
