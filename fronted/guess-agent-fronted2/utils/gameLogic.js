/**
 * 游戏逻辑和辅助函数
 */

// 难度等级配置
export const DIFFICULTY_LEVELS = {
  EASY: {
    key: "easy",
    label: "简单",
    value: 1,
    questionLimit: 15,
    guessLimit: 5,
  },
  MEDIUM: {
    key: "medium",
    label: "普通",
    value: 2,
    questionLimit: 10,
    guessLimit: 3,
  },
  HARD: {
    key: "hard",
    label: "困难",
    value: 3,
    questionLimit: 7,
    guessLimit: 2,
  },
};

// 游戏阶段
export const GAME_PHASES = {
  THINKING: "thinking", // AI思考中
  USER_TURN: "userTurn", // 用户回合
  AI_RESPONSE: "aiResponse", // AI回复中
  RESULT: "result", // 游戏结束
};

// 游戏状态
export const GAME_STATUS = {
  PLAYING: "playing",
  WON: "won",
  LOST: "lost",
};

/**
 * 创建新游戏对象
 */
export function createNewGame(startWord, difficulty) {
  const diffConfig = DIFFICULTY_LEVELS[difficulty] || DIFFICULTY_LEVELS.MEDIUM;

  return {
    id: generateGameId(),
    startWord,
    difficulty,
    questionsUsed: 0,
    questionLimit: diffConfig.questionLimit,
    guessesUsed: 0,
    guessLimit: diffConfig.guessLimit,
    roundNum: 0,
    startTime: Date.now(),
    messages: [], // 聊天消息
    status: GAME_STATUS.PLAYING,
    result: null,
  };
}

/**
 * 生成游戏ID
 */
export function generateGameId() {
  return `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 模拟AI响应（包含打字延迟）
 */
export function generateAIResponse(questionIndex, difficulty) {
  const responses = {
    1: "这取决于物体的特性。让我思考一下...",
    2: "有趣的角度。这涉及到...",
    3: "你在正确的方向上。",
    4: "不完全是，但你很接近...",
    5: "这与物理特性有关。",
    default: "你的提问很有启发性。",
  };

  return {
    text: responses[questionIndex] || responses.default,
    delay: 800 + Math.random() * 1200, // 800-2000ms随机延迟
  };
}

/**
 * 模拟AI"直觉"提示
 */
export function generateHunchHint(word) {
  const hints = {
    自行车: '"多考虑那些依靠人力而非热量的工具。"',
    钥匙: '"我打开了无数道门，却永远无法进入。"',
    雨伞: '"我是微风的无声伙伴，却能承载天空的泪滴。"',
    钉子: '"我很小，但可以承载很大的重量。"',
    书: '"我用文字滋养灵魂，却从不需要食物。"',
    灯: '"我点亮黑暗，却害怕火焰。"',
    default: '"思考这个物体的核心用途，而不是它的外观。"',
  };

  return hints[word] || hints.default;
}

/**
 * 计算AI信心指数 (0-100)
 */
export function calculateAIConfidence(
  roundNum,
  questionsUsed,
  guessesUsed,
  difficulty,
) {
  const baseConfidence = 100;
  const roundPenalty = roundNum * 3; // 每轮-3
  const questionBonus =
    (questionsUsed / DIFFICULTY_LEVELS[difficulty].questionLimit) * 20;
  const guessPenalty = guessesUsed * 10;

  const confidence = Math.max(
    30,
    Math.min(100, baseConfidence - roundPenalty + questionBonus - guessPenalty),
  );

  return Math.round(confidence);
}

/**
 * 验证游戏输入
 */
export function validateGameInput(input, type = "question") {
  const trimmed = input.trim();

  if (!trimmed) {
    return { valid: false, error: "输入不能为空" };
  }

  if (trimmed.length < 2) {
    return { valid: false, error: "输入过短" };
  }

  if (trimmed.length > 100) {
    return { valid: false, error: "输入过长" };
  }

  return { valid: true, error: null };
}

/**
 * 判断用户输入是问题还是猜测
 * 问题通常以"是"、"吗"、"呢"结尾或包含"是否"
 */
export function detectInputType(input) {
  const questionPatterns = [
    /[是吗呢？？]$/,
    /是否/,
    /能否/,
    /会不会/,
    /怎样/,
    /是什么/,
    /有没有/,
  ];

  const isQuestion = questionPatterns.some((pattern) => pattern.test(input));
  return isQuestion ? "question" : "guess";
}

/**
 * 格式化游戏时间
 */
export function formatGameTime(milliseconds) {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;

  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

/**
 * 创建游戏结果对象
 */
export function createGameResult(game, finalAnswer, isWon) {
  return {
    gameId: game.id,
    startWord: game.startWord,
    difficulty: game.difficulty,
    finalAnswer,
    isWon,
    roundsUsed: game.roundNum,
    questionsUsed: game.questionsUsed,
    guessesUsed: game.guessesUsed,
    totalTime: Date.now() - game.startTime,
    aiConfidence: calculateAIConfidence(
      game.roundNum,
      game.questionsUsed,
      game.guessesUsed,
      game.difficulty,
    ),
    timestamp: Date.now(),
    messageCount: game.messages.length,
  };
}
