/**
 * 应用全局常量
 */

// 应用配置
export const APP_CONFIG = {
  APP_NAME: "HUNCH - AI 单词游戏",
  VERSION: "1.0.0",
};

// 颜色系统
export const COLORS = {
  PRIMARY: "#006c5a",
  PRIMARY_CONTAINER: "#89f6da",
  PRIMARY_FIXED_DIM: "#7ae8cc",
  ON_PRIMARY: "#e4fff5",
  ON_PRIMARY_CONTAINER: "#005d4d",

  SECONDARY: "#1a6780",
  SECONDARY_CONTAINER: "#bbe9ff",
  SECONDARY_FIXED_DIM: "#9bdefa",
  ON_SECONDARY: "#f2faff",

  TERTIARY: "#6c5f18",
  TERTIARY_CONTAINER: "#feec95",
  TERTIARY_FIXED_DIM: "#efdd89",
  ON_TERTIARY: "#fff8ea",
  ON_TERTIARY_CONTAINER: "#63570f",

  SURFACE: "#f8f9fa",
  SURFACE_CONTAINER: "#ebeef0",
  SURFACE_CONTAINER_LOW: "#f1f4f5",
  SURFACE_CONTAINER_LOWEST: "#ffffff",
  SURFACE_CONTAINER_HIGH: "#e5e9eb",

  ON_SURFACE: "#2d3335",
  ON_SURFACE_VARIANT: "#5a6062",

  ERROR: "#a83836",
  ERROR_CONTAINER: "#fa746f",
  ON_ERROR_CONTAINER: "#6e0a12",

  OUTLINE: "#767c7e",
  OUTLINE_VARIANT: "#adb3b5",
};

// 难度标签
export const DIFFICULTY_LABELS = {
  easy: "简单",
  medium: "普通",
  hard: "困难",
};

// 游戏结果标签
export const RESULT_LABELS = {
  won: "获胜",
  lost: "落败",
};

// 提示信息
export const MESSAGES = {
  GAME_START_SUCCESS: "游戏开始！祝你好运",
  GAME_WON: "恭喜！你赢了！",
  GAME_LOST: "很遗憾，你输了",
  INPUT_EMPTY: "请输入内容",
  QUESTION_LIMIT_REACHED: "提问次数已用完",
  GUESS_LIMIT_REACHED: "猜测次数已用完",
};

// 示例AI提示
export const SAMPLE_HINTS = [
  '"多考虑那些依靠人力而非热量的工具。"',
  '"我是微风的无声伙伴，却能承载天空的泪滴。"',
  '"我打开了无数道门，却永远无法进入。"',
  '"我用文字滋养灵魂，却从不需要食物。"',
  '"思考这个物体的核心用途，而不是它的外观。"',
];

// 动画配置
export const ANIMATION_DURATION = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
};
