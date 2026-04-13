/**
 * 本地存储管理
 */

const STORAGE_KEYS = {
  GAME_HISTORY: "hunch_game_history",
  CURRENT_GAME: "hunch_current_game",
  USER_STATS: "hunch_user_stats",
};

/**
 * 保存游戏结果到历史记录
 */
export function saveGameResult(result) {
  try {
    const history = getGameHistory();
    history.unshift(result); // 添加到最前面

    // 只保存最近50场游戏
    if (history.length > 50) {
      history.pop();
    }

    uni.setStorageSync(STORAGE_KEYS.GAME_HISTORY, history);
    updateUserStats(result);

    return true;
  } catch (error) {
    console.error("保存游戏结果失败:", error);
    return false;
  }
}

/**
 * 获取游戏历史记录
 */
export function getGameHistory(filter = "all") {
  try {
    const history = uni.getStorageSync(STORAGE_KEYS.GAME_HISTORY) || [];

    if (filter === "all") {
      return history;
    } else if (filter === "won") {
      return history.filter((item) => item.isWon);
    } else if (filter === "lost") {
      return history.filter((item) => !item.isWon);
    }

    return history;
  } catch (error) {
    console.error("获取游戏历史失败:", error);
    return [];
  }
}

/**
 * 清除所有游戏历史
 */
export function clearGameHistory() {
  try {
    uni.removeStorageSync(STORAGE_KEYS.GAME_HISTORY);
    return true;
  } catch (error) {
    console.error("清除历史失败:", error);
    return false;
  }
}

/**
 * 保存当前游戏（用于意外中断恢复）
 */
export function saveCurrentGame(game) {
  try {
    uni.setStorageSync(STORAGE_KEYS.CURRENT_GAME, game);
    return true;
  } catch (error) {
    console.error("保存当前游戏失败:", error);
    return false;
  }
}

/**
 * 获取当前游戏
 */
export function getCurrentGame() {
  try {
    return uni.getStorageSync(STORAGE_KEYS.CURRENT_GAME) || null;
  } catch (error) {
    console.error("获取当前游戏失败:", error);
    return null;
  }
}

/**
 * 清除当前游戏
 */
export function clearCurrentGame() {
  try {
    uni.removeStorageSync(STORAGE_KEYS.CURRENT_GAME);
    return true;
  } catch (error) {
    console.error("清除当前游戏失败:", error);
    return false;
  }
}

/**
 * 更新用户统计数据
 */
function updateUserStats(result) {
  try {
    const stats = getUserStats();

    stats.totalGames++;
    if (result.isWon) {
      stats.winsCount++;
    } else {
      stats.lossesCount++;
    }

    // 按难度统计
    if (!stats.byDifficulty[result.difficulty]) {
      stats.byDifficulty[result.difficulty] = { played: 0, won: 0 };
    }
    stats.byDifficulty[result.difficulty].played++;
    if (result.isWon) {
      stats.byDifficulty[result.difficulty].won++;
    }

    // 最佳成绩
    if (result.isWon) {
      if (!stats.bestTime || result.totalTime < stats.bestTime) {
        stats.bestTime = result.totalTime;
      }
      if (!stats.minRounds || result.roundsUsed < stats.minRounds) {
        stats.minRounds = result.roundsUsed;
      }
    }

    stats.lastPlayTime = result.timestamp;

    uni.setStorageSync(STORAGE_KEYS.USER_STATS, stats);
  } catch (error) {
    console.error("更新用户统计失败:", error);
  }
}

/**
 * 获取用户统计数据
 */
export function getUserStats() {
  try {
    const stats = uni.getStorageSync(STORAGE_KEYS.USER_STATS);

    if (!stats) {
      return {
        totalGames: 0,
        winsCount: 0,
        lossesCount: 0,
        byDifficulty: {
          easy: { played: 0, won: 0 },
          medium: { played: 0, won: 0 },
          hard: { played: 0, won: 0 },
        },
        bestTime: null,
        minRounds: null,
        lastPlayTime: null,
      };
    }

    return stats;
  } catch (error) {
    console.error("获取用户统计失败:", error);
    return {};
  }
}

/**
 * 获取胜率
 */
export function getWinRate() {
  const stats = getUserStats();
  if (stats.totalGames === 0) return 0;
  return Math.round((stats.winsCount / stats.totalGames) * 100);
}

/**
 * 清除所有数据
 */
export function clearAllData() {
  try {
    uni.removeStorageSync(STORAGE_KEYS.GAME_HISTORY);
    uni.removeStorageSync(STORAGE_KEYS.CURRENT_GAME);
    uni.removeStorageSync(STORAGE_KEYS.USER_STATS);
    return true;
  } catch (error) {
    console.error("清除数据失败:", error);
    return false;
  }
}
