import { useState, useCallback, useRef } from "react";
import { gameApiClient } from "@/src/services/gameApiClient";
import {
  CreateGameRequest,
  SubmitTurnRequest,
  GameState,
  Message,
  HistoryItem,
} from "@/src/types/game";

interface UseGameReturn {
  gameState: GameState | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // 操作方法
  startGame: (
    userWord: string,
    difficulty: "easy" | "medium" | "hard",
  ) => Promise<void>;
  submitUserInput: (content: string) => Promise<void>;
  submitAnswer: (content: string) => Promise<void>;
  submitJudgement: (isCorrect: boolean) => Promise<void>;
  resetGame: () => void;
}

/**
 * 游戏逻辑 Hook - 管理游戏状态和 API 交互
 */
export function useGame(): UseGameReturn {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 用于记录游戏启动时间
  const startTimeRef = useRef<number | null>(null);

  /**
   * 启动新游戏
   */
  const startGame = useCallback(
    async (userWord: string, difficulty: "easy" | "medium" | "hard") => {
      setIsLoading(true);
      setError(null);
      setMessages([]);
      startTimeRef.current = Date.now();

      try {
        const createGameRequest: CreateGameRequest = {
          user_word: userWord,
          difficulty,
          owner_id: `player_${Date.now()}`, // 简单的用户标识
        };

        const response = await gameApiClient.createGame(createGameRequest);

        setGameState({
          gameId: response.game_id,
          status: response.status as
            | "active"
            | "finished_win"
            | "finished_loss",
          phase: "user_turn",
          roundCount: response.round_count,
          difficulty,
          history: [],
          currentUserWord: userWord,
          systemWordEncrypted: response.system_word_encrypted,
          createdAt: response.created_at,
          startTime: startTimeRef.current,
        });

        // 初始消息：等待用户提问
        setMessages([
          {
            role: "ai",
            content:
              '我已经想好一个词。请开始提问吧，记住我只能回答"是"或"不是"的问题。',
            timestamp: Date.now(),
            type: "chat",
          },
        ]);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "启动游戏失败";
        setError(errorMessage);
        console.error("Failed to start game:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  /**
   * 提交用户输入（提问或回答系统问题）
   * 根据当前phase自动判断是提问还是回答
   */
  const submitUserInput = useCallback(
    async (content: string) => {
      if (!gameState) {
        setError("游戏未启动");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // 记录前一阶段
        const previousPhase = gameState.phase;

        // 添加用户消息到本地
        setMessages((prev) => [
          ...prev,
          {
            role: "user",
            content,
            timestamp: Date.now(),
          },
        ]);

        // 根据当前phase确定turn_type
        // user_turn: 用户提问 -> turn_type: "input"
        // awaiting_answer: 用户回答系统问题 -> turn_type: "answer"
        const turnType = gameState.phase === "user_turn" ? "input" : "answer";

        const request: SubmitTurnRequest = {
          turn_type: turnType as "input" | "answer",
          content,
          mode: "agent",
        };

        const response = await gameApiClient.submitTurn(
          gameState.gameId,
          request,
        );

        // 更新游戏状态
        setGameState((prev) =>
          prev
            ? {
                ...prev,
                status: response.status as
                  | "active"
                  | "finished_win"
                  | "finished_loss",
                phase: response.phase,
                roundCount: response.history.length,
                history: response.history,
              }
            : null,
        );

        // 添加系统回答到本地消息
        if (response.response_text) {
          setMessages((prev) => [
            ...prev,
            {
              role: "ai",
              content: response.response_text || "",
              timestamp: Date.now(),
              type: "chat",
            },
          ]);
        }

        // 如果系统有新问题，添加系统问题到消息列表
        // 这通常在用户提问后出现（phase 从 user_turn 变为 awaiting_answer）
        if (response.system_question && response.phase === "awaiting_answer") {
          setMessages((prev) => [
            ...prev,
            {
              role: "ai",
              content: response.system_question || "",
              timestamp: Date.now(),
              type: "chat",
            },
          ]);
        }

        // 如果用户刚回答了系统的问题，系统已处理，提示用户继续提问或直接猜答案
        if (
          previousPhase === "awaiting_answer" &&
          response.phase === "user_turn"
        ) {
          setMessages((prev) => [
            ...prev,
            {
              role: "system",
              content: "回答已记录，轮到你继续提问或直接猜答案",
              timestamp: Date.now(),
              type: "notification",
            },
          ]);
        }

        // 检查游戏结束
        if (response.status !== "active") {
          console.log("Game ended:", response.status);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "提交失败";
        setError(errorMessage);
        console.error("Failed to submit input:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [gameState],
  );

  /**
   * 提交用户对系统问题的回答
   */
  const submitAnswer = useCallback(
    async (content: string) => {
      if (!gameState) {
        setError("游戏未启动");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        setMessages((prev) => [
          ...prev,
          {
            role: "user",
            content,
            timestamp: Date.now(),
          },
        ]);

        const request: SubmitTurnRequest = {
          turn_type: "answer",
          content,
          mode: "agent",
        };

        const response = await gameApiClient.submitTurn(
          gameState.gameId,
          request,
        );

        setGameState((prev) =>
          prev
            ? {
                ...prev,
                status: response.status as
                  | "active"
                  | "finished_win"
                  | "finished_loss",
                phase: response.phase,
                roundCount: response.history.length,
                history: response.history,
              }
            : null,
        );

        if (response.response_text) {
          setMessages((prev) => [
            ...prev,
            {
              role: "ai",
              content: response.response_text || "",
              timestamp: Date.now(),
            },
          ]);
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "提交回答失败";
        setError(errorMessage);
        console.error("Failed to submit answer:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [gameState],
  );

  /**
   * 提交对系统猜测的判断
   */
  const submitJudgement = useCallback(
    async (isCorrect: boolean) => {
      if (!gameState) {
        setError("游戏未启动");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const request: SubmitTurnRequest = {
          turn_type: "judge",
          judgement: isCorrect,
          mode: "agent",
        };

        const response = await gameApiClient.submitTurn(
          gameState.gameId,
          request,
        );

        setGameState((prev) =>
          prev
            ? {
                ...prev,
                status: response.status as
                  | "active"
                  | "finished_win"
                  | "finished_loss",
                phase: response.phase,
                roundCount: response.history.length,
                history: response.history,
              }
            : null,
        );

        if (response.response_text) {
          setMessages((prev) => [
            ...prev,
            {
              role: "ai",
              content: response.response_text || "",
              timestamp: Date.now(),
            },
          ]);
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "提交判断失败";
        setError(errorMessage);
        console.error("Failed to submit judgement:", err);
      } finally {
        setIsLoading(false);
      }
    },
    [gameState],
  );

  /**
   * 重置游戏
   */
  const resetGame = useCallback(() => {
    setGameState(null);
    setMessages([]);
    setError(null);
    startTimeRef.current = null;
  }, []);

  return {
    gameState,
    messages,
    isLoading,
    error,
    startGame,
    submitUserInput,
    submitAnswer,
    submitJudgement,
    resetGame,
  };
}
