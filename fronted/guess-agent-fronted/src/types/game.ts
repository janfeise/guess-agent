/**
 * 游戏相关的类型定义
 */

// ============ 请求类型 ============

export interface CreateGameRequest {
  owner_id?: string;
  user_word: string;
  difficulty?: "easy" | "medium" | "hard";
}

export interface SubmitTurnRequest {
  turn_type: "input" | "answer" | "judge";
  content?: string;
  question?: string; // 兼容旧客户端
  judgement?: boolean;
  mode?: "agent" | "helper";
}

// ============ 响应类型 ============

export interface HealthResponse {
  status: string;
  service: string;
  database: string;
  timestamp: string;
}

export interface CreateGameResponse {
  game_id: string;
  status: string;
  round_count: number;
  user_word: string;
  difficulty: string;
  system_word_encrypted: string;
  created_at: string;
}

export interface GameDetailProgress {
  phase: string;
  next_actor?: string;
  expected_turn_type?: string;
  waiting_answer?: boolean;
  awaiting_judgement?: boolean;
  pending_question?: string;
  pending_guess?: string;
  agent_confidence?: number;
  last_actor?: string;
  last_intent?: string | null;
}

export interface GameDetailsResponse {
  game_id: string;
  status: "active" | "finished";
  owner_id?: string | null;
  difficulty?: string | null;
  user_word?: string | null;
  round_count: number;
  summary: string;
  history: HistoryItem[];
  metadata: Record<string, unknown>;
  progress?: GameDetailProgress | null;
  created_at: string;
  updated_at: string;
  finished_at?: string | null;
  finish_reason?: string | null;
  system_word_encrypted?: string | null;
  target_word_source?: string | null;
}

export interface UserGameHistoryResponse {
  user_id: string;
  total: number;
  games: GameDetailsResponse[];
}

export interface HistoryItem {
  round_no: number;
  actor: "user" | "system";
  turn_type:
    | "question"
    | "answer"
    | "ask"
    | "guess"
    | "judge"
    | "judge_agent_guess";
  input_text?: string;
  answer_text?: string;
  answer_label?: "yes" | "no" | "unknown";
  hint?: string;
  confidence?: number;
  result?: string;
  source_word_owner?: "user" | "system";
  visible_to_agent?: boolean;
  visible_to_player?: boolean;
}

export interface SubmitTurnResponse {
  game_id: string;
  status: "active" | "finished";
  phase:
    | "user_turn"
    | "waiting_answer"
    | "awaiting_judgement"
    | "finished_win"
    | "finished_loss";
  result?: string;
  message?: string;
  answer?: "yes" | "no" | "unknown" | null;
  response_text?: string | null;
  answer_text?: string | null;
  system_question?: string | null; // 系统提问的内容
  hint?: string | null;
  confidence?: number;
  history?: HistoryItem[];
}

// ============ 错误类型 ============

export interface ErrorResponse {
  detail: string;
}

// ============ 游戏状态类型 ============

export interface GameState {
  gameId: string;
  status: "active" | "finished_win" | "finished_loss";
  phase: string;
  roundCount: number;
  difficulty: string;
  history: HistoryItem[];
  currentUserWord?: string;
  systemWordEncrypted?: string;
  createdAt?: string;
  startTime?: number;
  result?: string;
  finalMessage?: string;
  revealedWord?: string;
}

export type GameOutcome = "win" | "loss";

export interface GameEndStats {
  rounds: number;
  time: string;
  confidence?: number;
  message?: string;
  result?: string;
  revealedWord?: string;
}

// ============ UI 类型 ============

export interface Message {
  role: "ai" | "user" | "system";
  content: string;
  timestamp?: number;
  type?: "chat" | "notification"; // chat: 普通对话消息, notification: 提示通知
}

export interface GameConfig {
  word: string;
  difficulty: "easy" | "medium" | "hard" | "简单" | "普通" | "困难";
}
