import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import TopAppBar from "./components/TopAppBar";
import BottomNavBar from "./components/BottomNavBar";
import Home from "./pages/Home";
import Game from "./pages/Game";
import History from "./pages/History";
import Rules from "./pages/Rules";
import Result from "./pages/Result";

type Page = "home" | "game" | "history" | "rules" | "result";

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [gameConfig, setGameConfig] = useState({
    word: "",
    difficulty: "中等",
  });
  const [gameStats, setGameStats] = useState({ rounds: 0, time: "" });

  const [gamePageTitle, setGamePageTitle] = useState("Round 0"); // 游戏页面的标题

  const handleStartGame = (word: string, difficulty: string) => {
    setGameConfig({ word, difficulty });
    setCurrentPage("game");
  };

  const handleWin = (stats: { rounds: number; time: string }) => {
    setGameStats(stats);
    setCurrentPage("result");
  };

  const getTitle = () => {
    if (currentPage === "game") {
      return gamePageTitle;
    }

    return "";
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <Home onStartGame={handleStartGame} onNavigate={setCurrentPage} />
        );
      case "game":
        return (
          <Game
            difficulty={gameConfig.difficulty}
            userWord={gameConfig.word}
            onWin={handleWin}
            setGamePageTitle={setGamePageTitle}
          />
        );
      case "history":
        return <History />;
      case "rules":
        return <Rules onBack={() => setCurrentPage("game")} />;
      case "result":
        return (
          <Result
            stats={gameStats}
            onRestart={() => setCurrentPage("home")}
            onHome={() => setCurrentPage("home")}
          />
        );
      default:
        return (
          <Home onStartGame={handleStartGame} onNavigate={setCurrentPage} />
        );
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <TopAppBar title={getTitle()} />

      <main className="flex-1 min-h-0 px-6 max-w-screen-md mx-auto w-full">
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
      {["home", "history", "rules"].includes(currentPage) && (
        <BottomNavBar
          active={currentPage as "home" | "history" | "rules"}
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
