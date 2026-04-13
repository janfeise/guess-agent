import { Send, Bot, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useState, useRef, useEffect } from "react";
import ChatBubble from "@/src/components/ChatBubble";
import HunchCard from "@/src/components/HunchCard";
import { useGame } from "@/src/hooks/useGame";

interface GameProps {
  difficulty: string;
  userWord: string;
  onWin: (stats: { rounds: number; time: string }) => void;
}

export default function Game({ difficulty, userWord, onWin }: GameProps) {
  const { gameState, messages, isLoading, error, startGame, submitUserInput } =
    useGame();

  const [inputVal, setInputVal] = useState("");
  const [gameStarted, setGameStarted] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 映射难度等级
  const mapDifficulty = (diff: string): "easy" | "medium" | "hard" => {
    const diffMap: Record<string, "easy" | "medium" | "hard"> = {
      简单: "easy",
      easy: "easy",
      普通: "medium",
      medium: "medium",
      困难: "hard",
      hard: "hard",
    };
    return diffMap[diff] || "medium";
  };

  // 初始化游戏
  useEffect(() => {
    if (!gameStarted && userWord) {
      startGame(userWord, mapDifficulty(difficulty));
      setGameStarted(true);
    }
  }, [gameStarted, userWord, difficulty, startGame]);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // 处理游戏结束
  useEffect(() => {
    if (gameState && gameState.status === "finished_win") {
      const elapsedTime = gameState.startTime
        ? `${Math.floor((Date.now() - gameState.startTime) / 60000)}:${String(Math.floor(((Date.now() - gameState.startTime) % 60000) / 1000)).padStart(2, "0")}`
        : "0:00";

      setTimeout(() => {
        onWin({
          rounds: gameState.roundCount,
          time: elapsedTime,
        });
      }, 1500);
    }
  }, [gameState, onWin]);

  const handleSend = async () => {
    if (!inputVal.trim() || isLoading) return;

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
  const isAwaitingAnswer = currentPhase === "awaiting_answer";
  // 判断是否等待用户对系统猜测的判断
  const isAwaitingJudgement = currentPhase === "awaiting_judgement";

  return (
    <div className="flex flex-col h-[calc(100dvh-180px)]">
      {/* Status Bar */}
      <section className="px-1 py-4">
        <div className="flex items-center justify-between gap-4 py-4 px-6 bg-surface-container-low rounded-3xl">
          <div className="flex items-center gap-8">
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-on-surface-variant uppercase tracking-widest">
                当前进度
              </span>
              <span className="font-headline font-extrabold text-primary text-xl">
                第 {currentRound} 轮
              </span>
            </div>
            <div className="h-8 w-[1px] bg-outline-variant/20" />
            <div className="flex flex-col">
              <span className="text-[9px] font-bold text-on-surface-variant uppercase tracking-widest">
                挑战难度
              </span>
              <div className="flex items-center gap-2">
                <span className="font-headline font-bold text-on-surface text-sm">
                  {difficulty}
                </span>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                  <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                  <div className="w-1.5 h-1.5 rounded-full bg-outline-variant/30" />
                </div>
              </div>
            </div>
          </div>
          <div className="bg-primary-container px-4 py-2 rounded-full hidden sm:block">
            <span className="text-[10px] font-bold text-on-primary-container uppercase tracking-widest">
              {isUserTurn
                ? "你的回合"
                : isAwaitingAnswer
                  ? "等待你的回答"
                  : isAwaitingJudgement
                    ? "等待你的判断"
                    : "游戏进行中"}
            </span>
          </div>
        </div>
      </section>

      {/* Chat Area */}
      <main
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-1 py-6 space-y-8 scroll-smooth"
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
      <footer className="pt-4 pb-2">
        {error && (
          <div className="mb-3 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSend()}
              disabled={isLoading}
              className="w-full bg-surface-container-low border-none rounded-2xl py-5 px-6 focus:ring-2 focus:ring-primary/10 focus:bg-white transition-all text-base placeholder:text-on-surface-variant/40 disabled:opacity-50"
              placeholder={
                isLoading
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
            disabled={isLoading || !inputVal.trim()}
            className="btn-primary-gradient h-14 w-14 rounded-2xl flex items-center justify-center disabled:opacity-50"
          >
            <SendIcon className="w-6 h-6 fill-current" />
          </button>
        </div>

        {/* User Word Display */}
        {gameState?.currentUserWord && (
          <div className="mb-3 px-6 py-3 bg-primary-container/10 rounded-2xl flex items-center justify-between mt-5">
            <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">
              你的词
            </span>
            <span className="text-sm font-headline font-bold text-primary">
              {gameState.currentUserWord}
            </span>
          </div>
        )}
      </footer>
    </div>
  );
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}
