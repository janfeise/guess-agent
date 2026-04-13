<template>
  <view class="index-page">
    <TopBar @menu-click="handleMenuClick" />

    <view class="index-page__main">
      <!-- Hero Section -->
      <view class="hero">
        <view class="hero__badge">学科猜词大挑战</view>
        <view class="hero__title">
          Guess - Agent<br />
          <text class="hero__title--gradient">猜词游戏</text>
        </view>
        <text class="hero__subtitle">
          测试你与Guess Agent的直觉。你能跨越人类逻辑与 AI 推理之间的鸿沟吗？
        </text>
      </view>

      <!-- Start Game Card -->
      <view class="start-card">
        <view class="start-card__content">
          <!-- Start Word Input -->
          <view class="form-group">
            <label class="form-label">初始单词</label>
            <view class="form-input-wrapper">
              <input
                v-model="gameForm.startWord"
                class="form-input"
                placeholder="例如：大自然"
                maxlength="20"
              />
              <text class="form-input__icon">✏️</text>
            </view>
          </view>

          <!-- Difficulty Selector (Segmented Control) -->
          <view class="form-group">
            <label class="form-label">难度等级</label>
            <view class="segmented-control">
              <button
                v-for="(level, key) in difficultyLevels"
                :key="key"
                :class="[
                  'segmented-btn',
                  {
                    'segmented-btn--active': gameForm.difficulty === key,
                  },
                ]"
                @tap="gameForm.difficulty = key"
              >
                <text class="segmented-btn__text">{{ level.label }}</text>
              </button>
            </view>
          </view>

          <!-- Start Button -->
          <button
            class="btn-primary"
            @tap="handleStartGame"
            :loading="gameLoading"
            :disabled="!gameForm.startWord.trim() || gameLoading"
          >
            {{ gameLoading ? "加载中..." : "开始游戏 🚀" }}
          </button>
        </view>
      </view>

      <!-- Bento Grid: Recent Games + How to Play -->
      <view class="bento-grid">
        <!-- Recent Games -->
        <view class="bento-card bento-card--recent">
          <view class="bento-card__header">
            <text class="bento-header__icon">⏱️</text>
            <text class="bento-header__title">最近游戏</text>
          </view>
          <view v-if="recentGames.length > 0" class="recent-list">
            <view
              v-for="game in recentGames.slice(0, 2)"
              :key="game.gameId"
              class="recent-item"
              @tap="handleGameItemClick(game)"
            >
              <view class="recent-item__content">
                <text class="recent-item__word">{{ game.startWord }}</text>
                <text class="recent-item__meta">
                  {{ game.isWon ? "✅ 获胜" : "❌ 失败" }} •
                  {{ game.roundsUsed }} 轮
                </text>
              </view>
              <text class="recent-item__arrow">›</text>
            </view>
          </view>
          <view v-else class="recent-empty">
            <text>还没有游戏记录</text>
          </view>
        </view>

        <!-- How to Play -->
        <view class="bento-card bento-card--howto">
          <view class="bento-card__header">
            <text class="bento-header__icon">💡</text>
            <text class="bento-header__title">玩法说明</text>
          </view>
          <text class="howto-desc">
            从任意单词开始。AI
            将提供一个神秘的直觉。运用逻辑和发散性思维来缩小目标单词的范围。
          </text>
          <view class="howto-steps">
            <view class="step-dot">1</view>
            <view class="step-dot">2</view>
            <view class="step-dot">3</view>
          </view>
          <button class="btn-secondary" @tap="handleGoToRules">
            查看详细规则 →
          </button>
        </view>
      </view>

      <!-- AI Quote Card -->
      <view class="ai-quote-card">
        <view class="ai-quote__content">
          <text class="ai-quote__label">今日直觉</text>
          <text class="ai-quote__text">
            "它存在于寂静与地平线交汇之处，却无需半步即可远行。"
          </text>
        </view>
        <button class="ai-quote__btn">立即解决</button>
      </view>
    </view>

    <BottomNav />
  </view>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
// 注意：UniApp 环境通常使用内置的 uni.navigateTo 而非简单的 router.push
import TopBar from "../../components/TopBar.vue";
import BottomNav from "../../components/BottomNav.vue";
import { DIFFICULTY_LEVELS, createNewGame } from "../../utils/gameLogic";
import {
  getGameHistory,
  clearCurrentGame,
  saveCurrentGame,
} from "../../utils/storage";

const gameForm = reactive({
  startWord: "",
  difficulty: "medium",
});

const difficultyLevels = ref(DIFFICULTY_LEVELS);
const gameLoading = ref(false);
const recentGames = ref([]);

const handleStartGame = async () => {
  const word = gameForm.startWord.trim();
  if (!word) return;

  gameLoading.value = true;

  try {
    // 1. 创建游戏数据
    const newGame = createNewGame(word, gameForm.difficulty);

    // 2. 将新游戏数据持久化（推荐做法，比通过 getCurrentPages 调用方法更稳健）
    saveCurrentGame(newGame);

    uni.showToast({ title: "游戏开始！", icon: "success" });

    // 3. 跳转页面
    setTimeout(() => {
      uni.navigateTo({
        url: "/pages/gamePlay/gamePlay",
      });
    }, 800);
  } catch (error) {
    console.error("开始游戏失败:", error);
    uni.showToast({ title: "游戏启动失败", icon: "none" });
  } finally {
    gameLoading.value = false;
  }
};

const handleGameItemClick = (game) => {
  // 建议通过 URL 参数传递 ID，或者存储到本地存储
  uni.navigateTo({
    url: `/pages/result/result?id=${game.gameId}`,
  });
};

const handleGoToRules = () => {
  uni.switchTab({ url: "/pages/rules/rules" });
};

const handleMenuClick = () => {
  console.log("menu clicked");
};

const loadRecentGames = () => {
  recentGames.value = getGameHistory() || [];
};

onMounted(() => {
  loadRecentGames();
});
</script>

<style scoped lang="scss">
$primary: #006c5a;
$primary-container: #89f6da;
$tertiary: #6c5f18;
$tertiary-container: #feec95;
$on-primary: #e4fff5;
$on-surface: #2d3335;
$on-surface-variant: #5a6062;
$surface: #f8f9fa;
$surface-container-lowest: #ffffff;
$surface-container-low: #f1f4f5;
$outline-variant: #adb3b5;

.index-page {
  background-color: $surface;
  min-height: 100vh;
  padding-bottom: 180rpx;

  &__main {
    padding: 120rpx 24rpx 48rpx;
    max-width: 768rpx;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 48rpx;
  }
}

// ==================== Hero Section ====================
.hero {
  text-align: center;
  animation: fadeIn 0.6s ease-out;

  &__badge {
    display: inline-block;
    background-color: rgba($primary, 0.1);
    color: $primary;
    padding: 12rpx 24rpx;
    border-radius: 32rpx;
    font-size: 22rpx;
    font-weight: 700;
    letter-spacing: 2rpx;
    margin-bottom: 24rpx;
    text-transform: uppercase;
  }

  &__title {
    font-size: 64rpx;
    font-weight: 900;
    color: $on-surface;
    margin-bottom: 24rpx;
    line-height: 1.2;
    letter-spacing: -1rpx;
  }

  &__title--gradient {
    background: linear-gradient(135deg, $primary 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  &__subtitle {
    font-size: 28rpx;
    color: $on-surface-variant;
    line-height: 1.6;
    max-width: 520rpx;
    margin: 0 auto;
    font-weight: 500;
  }
}

// ==================== Start Card ====================
.start-card {
  background: linear-gradient(
    135deg,
    $surface-container-lowest 0%,
    rgba($primary, 0.02) 100%
  );
  border-radius: 32rpx;
  padding: 48rpx;
  box-shadow: 0 8px 32px rgba(45, 51, 53, 0.06);
  position: relative;
  overflow: hidden;

  &::before {
    content: "";
    position: absolute;
    top: -50rpx;
    right: -50rpx;
    width: 200rpx;
    height: 200rpx;
    background: rgba($primary-container, 0.15);
    border-radius: 50%;
    filter: blur(60rpx);
    pointer-events: none;
  }

  &__content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 36rpx;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.form-label {
  font-size: 24rpx;
  font-weight: 700;
  color: $on-surface;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  margin-left: 4rpx;
}

.form-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 20rpx 24rpx 20rpx 24rpx;
  background-color: $surface-container-low;
  border-radius: 20rpx;
  border: 2rpx solid transparent;
  font-size: 28rpx;
  color: $on-surface;
  transition: all 0.3s ease;

  &::placeholder {
    color: $outline-variant;
  }

  &:focus {
    border-color: $primary;
    box-shadow: 0 0 0 6rpx rgba($primary, 0.1);
  }
}

.form-input__icon {
  position: absolute;
  right: 24rpx;
  font-size: 32rpx;
  opacity: 0.4;
}

.segmented-control {
  display: flex;
  gap: 8rpx;
  padding: 8rpx;
  background-color: $surface-container-low;
  border-radius: 20rpx;
}

.segmented-btn {
  flex: 1;
  padding: 24rpx 8rpx;
  border: none;
  background-color: transparent;
  border-radius: 14rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: $on-surface-variant;
  transition: all 0.3s ease;
  text-transform: uppercase;

  &__text {
    display: block;
  }

  &--active {
    background-color: $surface-container-lowest;
    color: $primary;
    box-shadow: 0 2px 8px rgba($primary, 0.12);
    font-weight: 700;
  }

  &:active {
    transform: scale(0.95);
  }
}

.btn-primary {
  width: 100%;
  padding: 28rpx 32rpx;
  background: linear-gradient(135deg, $primary 0%, #00826a 100%);
  color: $on-primary;
  border: none;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 700;
  letter-spacing: 1rpx;
  box-shadow: 0 12px 32px rgba($primary, 0.25);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;

  &:active:not(:disabled) {
    transform: scale(0.98);
    box-shadow: 0 6px 16px rgba($primary, 0.15);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

// ==================== Bento Grid ====================
.bento-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24rpx;

  @media (min-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.bento-card {
  background-color: $surface-container-lowest;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 4px 16px rgba(45, 51, 53, 0.04);
  transition: all 0.3s ease;

  &:active {
    transform: translateY(-2rpx);
    box-shadow: 0 8px 24px rgba(45, 51, 53, 0.08);
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 24rpx;
  }

  &--recent {
    background-color: $surface-container-low;
  }

  &--howto {
    background: linear-gradient(
      135deg,
      rgba($tertiary-container, 0.2) 0%,
      rgba($tertiary-container, 0.05) 100%
    );
  }
}

.bento-header__icon {
  font-size: 36rpx;
}

.bento-header__title {
  font-size: 28rpx;
  font-weight: 700;
  color: $on-surface;
}

// ---- Recent Games ----
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background-color: $surface-container-lowest;
  border-radius: 16rpx;
  transition: all 0.3s ease;

  &:active {
    transform: translateX(4rpx);
    background-color: rgba($primary, 0.05);
  }
}

.recent-item__content {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex: 1;
}

.recent-item__word {
  font-size: 26rpx;
  font-weight: 700;
  color: $on-surface;
}

.recent-item__meta {
  font-size: 20rpx;
  color: $on-surface-variant;
}

.recent-item__arrow {
  font-size: 32rpx;
  color: $primary;
  opacity: 0.5;
  margin-left: 12rpx;
}

.recent-empty {
  padding: 40rpx 20rpx;
  text-align: center;
  color: $on-surface-variant;
  font-size: 24rpx;
}

// ---- How to Play ----
.howto-desc {
  font-size: 24rpx;
  color: $on-surface-variant;
  line-height: 1.6;
  margin-bottom: 24rpx;
}

.howto-steps {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.step-dot {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background-color: $tertiary-container;
  color: #3f3300;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 24rpx;

  &:nth-child(2) {
    opacity: 0.65;
  }

  &:nth-child(3) {
    opacity: 0.35;
  }
}

.btn-secondary {
  width: 100%;
  padding: 16rpx 24rpx;
  background-color: transparent;
  color: $on-surface;
  border: 2rpx solid $outline-variant;
  border-radius: 16rpx;
  font-size: 24rpx;
  font-weight: 600;
  transition: all 0.3s ease;

  &:active {
    background-color: rgba($primary, 0.05);
    border-color: $primary;
    color: $primary;
  }
}

// ==================== AI Quote Card ====================
.ai-quote-card {
  background: linear-gradient(
    135deg,
    rgba($primary, 0.08) 0%,
    rgba($primary-container, 0.08) 100%
  );
  border: 1rpx solid rgba($primary, 0.15);
  border-radius: 28rpx;
  padding: 40rpx;
  backdrop-filter: blur(20rpx);
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  align-items: flex-start;
}

.ai-quote__content {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  flex: 1;
}

.ai-quote__label {
  font-size: 20rpx;
  font-weight: 700;
  color: $primary;
  text-transform: uppercase;
  letter-spacing: 2rpx;
}

.ai-quote__text {
  font-size: 28rpx;
  color: $on-surface;
  line-height: 1.8;
  font-style: italic;
  font-weight: 500;
}

.ai-quote__btn {
  padding: 16rpx 32rpx;
  background-color: #bbe9ff;
  color: #004559;
  border: none;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 700;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.96);
    opacity: 0.9;
  }
}

// ==================== Animations ====================
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
