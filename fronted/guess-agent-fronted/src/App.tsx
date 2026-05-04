import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import TopAppBar from "./components/TopAppBar";
import BottomNavBar from "./components/BottomNavBar";
import Home from "./pages/Home";
import Game from "./pages/Game";
import History from "./pages/History";
import ProjectIntro from "./pages/ProjectIntro.tsx";
import Result from "./pages/Result";
import { GameEndStats, GameOutcome } from "@/src/types/game";

type Page = "home" | "game" | "history" | "project" | "result";

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [selectedGameId, setSelectedGameId] = useState<string | null>(null);
  const [gameConfig, setGameConfig] = useState({
    word: "",
    difficulty: "中等",
  });
  const [gameResult, setGameResult] = useState<{
    outcome: GameOutcome;
    stats: GameEndStats;
  } | null>(null);

  const [gamePageTitle, setGamePageTitle] = useState("Round 0"); // 游戏页面的标题

  const handleStartGame = (word: string, difficulty: string) => {
    setGameConfig({ word, difficulty });
    setGameResult(null);
    setSelectedGameId(null);
    setCurrentPage("game");
  };

  const handleOpenGame = (gameId: string) => {
    setSelectedGameId(gameId);
    setGameResult(null);
    setCurrentPage("game");
  };

  const handleGameEnd = (outcome: GameOutcome, stats: GameEndStats) => {
    setGameResult({ outcome, stats });
    setCurrentPage("result");
  };

  const getTitle = () => {
    if (currentPage === "game") {
      return gamePageTitle;
    }

    if (currentPage === "project") {
      return " ";
    }

    return "";
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <Home
            onStartGame={handleStartGame}
            onNavigate={setCurrentPage}
            onOpenGame={handleOpenGame}
          />
        );
      case "game":
        return (
          <Game
            difficulty={gameConfig.difficulty}
            userWord={gameConfig.word}
            gameId={selectedGameId}
            onGameEnd={handleGameEnd}
            setGamePageTitle={setGamePageTitle}
            onBackToHistory={() => setCurrentPage("history")}
          />
        );
      case "history":
        return <History onOpenGame={handleOpenGame} />;
      case "project":
        return <ProjectIntro onBack={() => setCurrentPage("home")} />;
      case "result":
        return (
          <Result
            outcome={gameResult?.outcome ?? "win"}
            stats={gameResult?.stats ?? { rounds: 0, time: "0:00" }}
            onRestart={() => setCurrentPage("home")}
            onHome={() => setCurrentPage("home")}
          />
        );
      default:
        return (
          <Home
            onStartGame={handleStartGame}
            onNavigate={setCurrentPage}
            onOpenGame={handleOpenGame}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <TopAppBar title={getTitle()} />

      <main className="flex-1 min-h-0 px-6 max-w-screen-md mx-auto w-full pb-55">
        <AnimatePresence mode="wait">
          <motion.div
            className="h-screen w-full"
            key={currentPage}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Only show bottom nav on main pages */}
      {["home", "history", "project"].includes(currentPage) && (
        <BottomNavBar
          active={currentPage as "home" | "history" | "project"}
          onNavigate={setCurrentPage}
        />
      )}

      {/* Background Decoration */}
      <div className="fixed inset-0 -z-10 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 -left-20 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 -right-20 w-[500px] h-[500px] bg-tertiary/5 rounded-full blur-[120px]" />
      </div>
    </div>
  );
}
