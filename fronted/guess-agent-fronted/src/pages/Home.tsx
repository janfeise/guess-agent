import {
  Rocket,
  History as HistoryIcon,
  ChevronRight,
  Lightbulb,
} from "lucide-react";
import { motion } from "motion/react";
import { useState, useEffect } from "react";
import { gameApiClient } from "@/src/services/gameApiClient";

interface HomeProps {
  onStartGame: (word: string, difficulty: string) => void;
  onNavigate: (page: "history" | "rules") => void;
}

interface RecentGame {
  name: string;
  result: string;
  rounds: number | string;
}

export default function Home({ onStartGame, onNavigate }: HomeProps) {
  const [startWord, setStartWord] = useState("");
  const [difficulty, setDifficulty] = useState("普通");
  const [recentGames, setRecentGames] = useState<RecentGame[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<"online" | "offline" | "checking">(
    "checking",
  );

  // 检查后端连接
  useEffect(() => {
    const checkApiConnection = async () => {
      setApiStatus("checking");
      try {
        await gameApiClient.checkHealth();
        setApiStatus("online");
        console.log("✓ 后端服务连接成功");
      } catch (err) {
        setApiStatus("offline");
        console.warn("✗ 后端服务离线：", err);
      }
    };

    checkApiConnection();
    // 每 30 秒检查一次连接
    const interval = setInterval(checkApiConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // 加载最近游戏历史（暂时使用模拟数据）
  useEffect(() => {
    // TODO: 当后端提供游戏历史 API 时，替换为真实数据
    // 目前使用本地存储或模拟数据
    const mockGames: RecentGame[] = [
      { name: "星云", result: "获胜", rounds: 4 },
      { name: "合成", result: "失败", rounds: "AI 获胜" },
    ];
    setRecentGames(mockGames);
  }, []);

  const handleStartGame = async () => {
    if (!startWord.trim()) {
      alert("请输入一个词");
      return;
    }

    if (apiStatus !== "online") {
      alert("后端服务未连接，请检查服务状态");
      return;
    }

    setIsLoading(true);
    try {
      onStartGame(startWord, difficulty);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-12 pb-12">
      {/* API 状态指示器 */}
      {apiStatus !== "online" && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 rounded-lg bg-yellow-100 text-yellow-800 text-sm font-medium"
        >
          {apiStatus === "checking"
            ? "🔄 正在检查后端服务..."
            : "⚠️ 后端服务离线，游戏功能将受影响"}
        </motion.div>
      )}

      {/* Hero Section */}
      <section className="text-center space-y-6 pt-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/5 text-primary font-bold text-[10px] tracking-[0.2em] uppercase"
        >
          学科猜词大挑战
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-5xl font-extrabold tracking-tight text-on-surface leading-tight font-headline"
        >
          DeepSeek - AI <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
            猜词游戏
          </span>
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-on-surface-variant max-w-xs mx-auto font-medium leading-relaxed"
        >
          测试你与Guess Agent的直觉。你能跨越人类逻辑与 AI 推理之间的鸿沟吗？
        </motion.p>
      </section>

      {/* Start Game Card */}
      <motion.section
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-surface-container-lowest rounded-[2.5rem] p-8 shadow-[0_12px_40px_rgba(0,0,0,0.04)] relative overflow-hidden"
      >
        <div className="absolute -right-12 -top-12 w-32 h-32 bg-primary-container/20 rounded-full blur-3xl" />
        <div className="space-y-8 relative z-10">
          <div className="space-y-6">
            <div className="space-y-3">
              <label className="text-[10px] font-bold text-on-surface-variant ml-1 uppercase tracking-widest">
                初始单词
              </label>
              <div className="relative group">
                <input
                  value={startWord}
                  onChange={(e) => setStartWord(e.target.value)}
                  disabled={apiStatus !== "online" || isLoading}
                  className="w-full bg-surface-container-low border-none rounded-2xl py-5 px-6 text-lg focus:ring-2 focus:ring-primary/10 transition-all placeholder:text-outline-variant/50 disabled:opacity-50"
                  placeholder="例如：大自然"
                  type="text"
                />
              </div>
            </div>
            <div className="space-y-3">
              <label className="text-[10px] font-bold text-on-surface-variant ml-1 uppercase tracking-widest">
                难度等级
              </label>
              <div className="flex p-1.5 bg-surface-container-low rounded-2xl">
                {["简单", "普通", "困难"].map((d) => (
                  <button
                    key={d}
                    onClick={() => setDifficulty(d)}
                    disabled={apiStatus !== "online" || isLoading}
                    className={`flex-1 py-3 px-2 rounded-xl text-xs font-bold transition-all disabled:opacity-50 ${
                      difficulty === d
                        ? "text-primary bg-white shadow-sm"
                        : "text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <button
            onClick={handleStartGame}
            disabled={apiStatus !== "online" || isLoading || !startWord.trim()}
            className="w-full py-5 rounded-[1.5rem] btn-primary-gradient text-xl font-bold tracking-tight flex items-center justify-center gap-3 disabled:opacity-50"
          >
            {isLoading ? "启动中..." : "开始游戏"}
            <Rocket className="w-6 h-6" />
          </button>
        </div>
      </motion.section>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent Games */}
        <section className="bg-surface-container-low rounded-[2rem] p-6 space-y-6">
          <div className="flex justify-between items-center px-1">
            <h3 className="font-bold text-lg flex items-center gap-2 font-headline">
              <HistoryIcon className="w-5 h-5 text-primary" />
              最近游戏
            </h3>
          </div>
          <div className="space-y-3">
            {recentGames.length > 0 ? (
              recentGames.map((game, i) => (
                <div
                  key={i}
                  onClick={() => onNavigate("history")}
                  className="bg-white p-5 rounded-2xl flex items-center justify-between group cursor-pointer hover:translate-x-1 transition-all shadow-sm"
                >
                  <div>
                    <div className="font-bold text-on-surface">{game.name}</div>
                    <div className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider mt-1">
                      {game.result} • {game.rounds} 回合
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-primary/40 group-hover:text-primary transition-colors" />
                </div>
              ))
            ) : (
              <div className="bg-white p-5 rounded-2xl text-center text-on-surface-variant">
                暂无游戏记录
              </div>
            )}
          </div>
        </section>

        {/* How to Play */}
        <section className="bg-tertiary-container/20 rounded-[2rem] p-6 space-y-4 relative overflow-hidden">
          <h3 className="font-bold text-lg flex items-center gap-2 font-headline">
            <Lightbulb className="w-5 h-5 text-tertiary" />
            玩法说明
          </h3>
          <p className="text-sm text-on-surface-variant leading-relaxed font-medium">
            从任意单词开始。AI
            将提供一个神秘的直觉。运用逻辑和发散性思维来缩小目标单词的范围。
          </p>
          <div className="flex gap-2 pt-4">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className="w-8 h-8 rounded-full bg-tertiary/10 flex items-center justify-center text-[10px] font-bold text-tertiary"
              >
                {s}
              </div>
            ))}
          </div>
          <SparklesIcon className="absolute -bottom-6 -right-6 w-32 h-32 text-tertiary/5" />
        </section>
      </div>
    </div>
  );
}

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M19,1L17.74,3.74L15,5L17.74,6.26L19,9L20.26,6.26L23,5L20.26,3.74L19,1M9,4L6.5,9.5L1,12L6.5,14.5L9,20L11.5,14.5L17,12L11.5,9.5L9,4M19,15L17.74,17.74L15,19L17.74,20.26L19,23L20.26,20.26L23,19L20.26,17.74L19,15Z" />
    </svg>
  );
}
