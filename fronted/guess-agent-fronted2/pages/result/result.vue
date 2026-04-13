<template>
  <view class="result-page">
    <TopBar />

    <view class="result-page__container">
      <!-- Victory/Defeat Banner -->
      <view class="banner" :class="{ 'banner--won': gameResult.isWon }">
        <view class="banner__badge">
          <text class="badge-icon">{{ gameResult.isWon ? "🏆" : "〽️" }}</text>
          <text class="badge-text">{{
            gameResult.isWon ? "挑战完成" : "挑战未完成"
          }}</text>
        </view>
        <text class="banner__title">{{
          gameResult.isWon ? "胜利" : "失败"
        }}</text>
        <text class="banner__subtitle">
          {{
            gameResult.isWon
              ? "以太向导对此印象深刻。你的直觉在未知中开辟了一条道路。"
              : "很遗憾，你这次没有成功。但每次尝试都是学习的机会！"
          }}
        </text>
      </view>

      <!-- Result Grid -->
      <view class="result-grid">
        <!-- Target Word Card -->
        <view class="target-card">
          <text class="target-label">正确答案：</text>
          <text class="target-word">{{ gameResult.finalAnswer }}</text>
          <view class="target-icon">{{
            getTargetIcon(gameResult.finalAnswer)
          }}</view>
        </view>

        <!-- Stats Cards -->
        <view class="stats-grid">
          <ResultCard
            label="使用轮次"
            :value="gameResult.roundsUsed"
            icon="🔄"
          />
          <ResultCard
            label="总用时"
            :value="formatTime(gameResult.totalTime)"
            icon="⏱️"
          />
          <ResultCard
            label="AI 信心指数"
            :value="`${gameResult.aiConfidence}%`"
            icon="🧠"
          />
          <ResultCard
            label="提问次数"
            :value="gameResult.questionsUsed"
            icon="❓"
          />
        </view>
      </view>

      <!-- Action Buttons -->
      <view class="action-buttons">
        <button class="btn btn--primary" @click="handlePlayAgain">
          再玩一次 🎮
        </button>
        <button class="btn btn--secondary" @click="handleBackHome">
          返回首页 🏠
        </button>
      </view>

      <!-- Share Stats -->
      <view class="share-section">
        <view class="share-title">分享你的成绩</view>
        <view class="share-stats">
          <text
            >我在 HUNCH 中答对了这个词，用时
            {{ formatTime(gameResult.totalTime) }}！</text
          >
        </view>
      </view>
    </view>

    <BottomNav />
  </view>
</template>

<script setup>
import { ref } from "vue";
import TopBar from "../../components/TopBar.vue";
import ResultCard from "../../components/ResultCard.vue";
import BottomNav from "../../components/BottomNav.vue";

const gameResult = ref({
  gameId: "",
  startWord: "",
  difficulty: "medium",
  finalAnswer: "",
  isWon: false,
  roundsUsed: 0,
  questionsUsed: 0,
  guessesUsed: 0,
  totalTime: 0,
  aiConfidence: 0,
  timestamp: Date.now(),
});

const showGameResult = (result) => {
  gameResult.value = result;
};

// Make this available to page stack
if (typeof getCurrentPages === "function") {
  const currentPageInstance = getCurrentPages()[getCurrentPages().length - 1];
  if (currentPageInstance) {
    currentPageInstance.showGameResult = showGameResult;
  }
}

const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
};

const getTargetIcon = (word) => {
  const icons = {
    自行车: "🚴",
    钥匙: "🔑",
    雨伞: "☂️",
    钉子: "🔧",
    书: "📚",
    灯: "💡",
    default: "✨",
  };
  return icons[word] || icons.default;
};

const handlePlayAgain = () => {
  uni.switchTab({
    url: "/pages/index/index",
  });
};

const handleBackHome = () => {
  uni.switchTab({
    url: "/pages/index/index",
  });
};
</script>

<style scoped lang="scss">
.result-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: 100rpx;

  &__container {
    flex: 1;
    padding-top: 80rpx;
    padding-left: 24rpx;
    padding-right: 24rpx;
    max-width: 768rpx;
    margin: 0 auto;
  }
}

.banner {
  text-align: center;
  margin-bottom: 48rpx;
  padding: 32rpx;
  background-color: rgba(137, 246, 218, 0.1);
  border-radius: 32rpx;
  transition: all 0.3s ease;

  &--won {
    background-color: #d1fae5;
  }

  &__badge {
    display: inline-flex;
    align-items: center;
    gap: 8rpx;
    background-color: #89f6da;
    color: #005d4d;
    padding: 12rpx 16rpx;
    border-radius: 24rpx;
    margin-bottom: 16rpx;
    font-size: 20rpx;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1rpx;
  }

  .badge-icon {
    font-size: 24rpx;
  }

  &__title {
    display: block;
    font-size: 72rpx;
    font-weight: 900;
    color: #006c5a;
    margin-bottom: 16rpx;
    font-family: "Plus Jakarta Sans", sans-serif;
    letter-spacing: 2rpx;
  }

  &__subtitle {
    font-size: 24rpx;
    color: #5a6062;
    line-height: 1.6;
    max-width: 500rpx;
    margin: 0 auto;
  }
}

.result-grid {
  margin-bottom: 48rpx;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24rpx;
}

.target-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 32rpx;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 12rpx 40rpx rgba(45, 51, 53, 0.06);
}

.target-label {
  display: block;
  font-size: 20rpx;
  color: #5a6062;
  text-transform: uppercase;
  letter-spacing: 2rpx;
  margin-bottom: 8rpx;
}

.target-word {
  display: block;
  font-size: 56rpx;
  font-weight: 900;
  color: #2d3335;
  letter-spacing: 2rpx;
  margin-bottom: 16rpx;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.target-icon {
  font-size: 40rpx;
  opacity: 0.5;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 48rpx;
}

.btn {
  padding: 20rpx;
  border: none;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1rpx;

  &--primary {
    background: linear-gradient(135deg, #006c5a 0%, #7ae8cc 100%);
    color: #e4fff5;
    box-shadow: 0 12rpx 40rpx rgba(0, 108, 90, 0.2);

    &:active {
      transform: scale(0.98);
    }
  }

  &--secondary {
    background-color: #bbe9ff;
    color: #005971;

    &:active {
      opacity: 0.9;
    }
  }
}

.share-section {
  background-color: rgba(222, 227, 230, 0.4);
  backdrop-filter: blur(20px);
  border-radius: 16rpx;
  padding: 24rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.share-title {
  font-size: 20rpx;
  font-weight: 700;
  color: #2d3335;
  text-transform: uppercase;
  letter-spacing: 2rpx;
  margin-bottom: 12rpx;
}

.share-stats {
  font-size: 24rpx;
  color: #2d3335;
  line-height: 1.6;
}
</style>
