<template>
  <view class="game-play-page">
    <TopBar />

    <view class="game-play-page__header">
      <view class="game-status-bar">
        <view class="status-item">
          <text class="status-label">当前进度</text>
          <text class="status-value">第 {{ currentGame.roundNum }} 轮</text>
        </view>
        <view class="divider"></view>
        <view class="status-item">
          <text class="status-label">挑战信息</text>
          <view class="difficulty-info">
            <text>难度: {{ difficultyLabel }}</text>
            <view class="difficulty-dots">
              <view
                v-for="i in 3"
                :key="i"
                class="dot"
                :class="{ 'dot--active': i <= difficultyLevel }"
              ></view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Chat Messages Area -->
    <view class="messages-container">
      <view
        v-if="!currentGame || messages.length === 0"
        class="welcome-section"
      >
        <text class="welcome-text">欢迎开始游戏！🎮</text>
        <text class="welcome-subtitle">与空灵向导开始对话吧</text>
      </view>

      <view
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-wrapper"
        :class="{ 'message-wrapper--user': msg.type === 'user' }"
      >
        <ChatBubble :message="msg.text" :type="msg.type" />
      </view>

      <!-- Hunch Card (appears periodically) -->
      <view v-if="showHunchCard" class="hunch-wrapper">
        <HunchCard :hintText="hunchHint" />
      </view>

      <view v-if="isLoading" class="loading-indicator">
        <text class="loading-dot">●</text>
        <text class="loading-dot">●</text>
        <text class="loading-dot">●</text>
      </view>
    </view>

    <!-- Input Area -->
    <view class="input-area">
      <view class="input-wrapper">
        <input
          v-model="userInput"
          class="user-input"
          placeholder="提问或尝试猜测..."
          @focus="handleInputFocus"
        />
      </view>
      <button
        class="submit-btn"
        @click="handleSubmitMessage"
        :disabled="!userInput.trim() || isLoading"
      >
        ➤
      </button>
    </view>

    <!-- Game Info Footer -->
    <view class="game-footer">
      <text class="footer-text">
        提问: {{ currentGame.questionsUsed }} /
        {{ currentGame.questionLimit }} | 猜测: {{ currentGame.guessesUsed }} /
        {{ currentGame.guessLimit }}
      </text>
    </view>

    <BottomNav />
  </view>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from "vue";
import TopBar from "../../components/TopBar.vue";
import ChatBubble from "../../components/ChatBubble.vue";
import HunchCard from "../../components/HunchCard.vue";
import BottomNav from "../../components/BottomNav.vue";
import {
  DIFFICULTY_LEVELS,
  generateAIResponse,
  generateHunchHint,
  detectInputType,
  createGameResult,
  calculateAIConfidence,
} from "../../utils/gameLogic";
import { saveCurrentGame, saveGameResult } from "../../utils/storage";

// Game state
const currentGame = reactive({
  startWord: "",
  difficulty: "medium",
  questionsUsed: 0,
  questionLimit: 10,
  guessesUsed: 0,
  guessLimit: 3,
  roundNum: 0,
  status: "playing",
});

const messages = ref([]);
const userInput = ref("");
const isLoading = ref(false);
const showHunchCard = ref(false);
const hunchHint = ref("");
const scrollViewId = ref("messages-scroll");

const difficultyLabel = computed(() => {
  return DIFFICULTY_LEVELS[currentGame.difficulty]?.label || "普通";
});

const difficultyLevel = computed(() => {
  const levels = { easy: 1, medium: 2, hard: 3 };
  return levels[currentGame.difficulty] || 2;
});

// Initialize game with data from previous page
const initGame = (game) => {
  Object.assign(currentGame, game);
  currentGame.roundNum = 1;

  // Initial AI message
  const welcomeMsg = `我想到了一个词。你初始给的是"${game.startWord}"。我已经基于此思考了一个相关的词。你准备好了吗？`;
  messages.value.push({
    type: "agent",
    text: welcomeMsg,
  });

  saveCurrentGame(currentGame);
};

// Make this available to the page stack
if (typeof getCurrentPages === "function") {
  const currentPageInstance = getCurrentPages()[getCurrentPages().length - 1];
  if (currentPageInstance) {
    currentPageInstance.initGame = initGame;
  }
}

const handleInputFocus = () => {
  nextTick(() => {
    // Scroll to bottom
    uni.pageScrollTo({
      scrollTop: 10000,
      duration: 300,
    });
  });
};

const handleSubmitMessage = async () => {
  const trimmedInput = userInput.value.trim();

  if (!trimmedInput) {
    uni.showToast({
      title: "请输入内容",
      icon: "none",
    });
    return;
  }

  // Detect input type
  const inputType = detectInputType(trimmedInput);

  // Check limits
  if (
    inputType === "question" &&
    currentGame.questionsUsed >= currentGame.questionLimit
  ) {
    uni.showToast({
      title: "提问次数已用完",
      icon: "none",
    });
    return;
  }

  if (
    inputType === "guess" &&
    currentGame.guessesUsed >= currentGame.guessLimit
  ) {
    uni.showToast({
      title: "猜测次数已用完",
      icon: "none",
    });
    return;
  }

  // Add user message
  messages.value.push({
    type: "user",
    text: trimmedInput,
  });

  // Update counts
  if (inputType === "question") {
    currentGame.questionsUsed++;
  } else {
    currentGame.guessesUsed++;
  }

  userInput.value = "";
  isLoading.value = true;

  try {
    // Simulate AI thinking time
    await new Promise((resolve) =>
      setTimeout(resolve, 800 + Math.random() * 1200),
    );

    // Generate AI response
    const aiResponse = generateAIResponse(
      currentGame.questionsUsed,
      currentGame.difficulty,
    );

    // Add AI message
    messages.value.push({
      type: "agent",
      text: aiResponse.text,
    });

    currentGame.roundNum++;

    // Show hunch hint occasionally (every 2-3 questions)
    if (currentGame.questionsUsed % 3 === 0 && currentGame.questionsUsed > 0) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      showHunchCard.value = true;
      hunchHint.value = generateHunchHint(currentGame.startWord);

      // Hide hunch card after display
      setTimeout(() => {
        showHunchCard.value = false;
      }, 4000);
    }

    // Check for win condition (simplified - when guess limit reached without correct guess)
    if (inputType === "guess") {
      // Simulate win/loss logic
      const isCorrect = Math.random() > 0.5; // Random for demo

      if (isCorrect) {
        // Win!
        await new Promise((resolve) => setTimeout(resolve, 300));
        messages.value.push({
          type: "agent",
          text: "恭喜！你猜对了！🎉",
        });

        currentGame.status = "won";

        // Create result
        const result = createGameResult(currentGame, "TARGET_WORD", true);
        saveGameResult(result);

        setTimeout(() => {
          navigateToResult(result, true);
        }, 1500);
      } else if (currentGame.guessesUsed >= currentGame.guessLimit) {
        // Loss - out of guesses
        messages.value.push({
          type: "agent",
          text: "遗憾的是，你用完了所有猜测机会。游戏结束！",
        });

        currentGame.status = "lost";
        const result = createGameResult(currentGame, "TARGET_WORD", false);
        saveGameResult(result);

        setTimeout(() => {
          navigateToResult(result, false);
        }, 1500);
      } else {
        messages.value.push({
          type: "agent",
          text: "不对呢。再试试？",
        });
      }
    }

    saveCurrentGame(currentGame);
  } catch (error) {
    console.error("Error processing message:", error);
    uni.showToast({
      title: "处理失败，请重试",
      icon: "none",
    });
  } finally {
    isLoading.value = false;
    nextTick(() => {
      handleInputFocus();
    });
  }
};

const navigateToResult = (result, isWon) => {
  uni.navigateTo({
    url: "/pages/result/result",
    success: () => {
      const pages = getCurrentPages();
      const resultPage = pages[pages.length - 1];
      resultPage.showGameResult(result);
    },
  });
};

onMounted(() => {
  // Game init will be called from index page
  console.log("GamePlay page mounted");
});

onUnmount(() => {
  console.log("GamePlay page unmounted");
});
</script>

<style scoped lang="scss">
.game-play-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: 120rpx;

  &__header {
    padding-top: 80rpx;
    padding-left: 24rpx;
    padding-right: 24rpx;
    padding-bottom: 16rpx;
  }
}

.game-status-bar {
  background-color: #f1f4f5;
  border-radius: 16rpx;
  padding: 12rpx 24rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  justify-content: space-between;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.status-label {
  font-size: 16rpx;
  color: #5a6062;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  font-weight: 600;
}

.status-value {
  font-size: 28rpx;
  color: #006c5a;
  font-weight: 900;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.difficulty-info {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #2d3335;
  font-weight: 600;
}

.difficulty-dots {
  display: flex;
  gap: 4rpx;
}

.dot {
  width: 6rpx;
  height: 6rpx;
  border-radius: 50%;
  background-color: #adb3b5;

  &--active {
    background-color: #006c5a;
  }
}

.divider {
  width: 1rpx;
  height: 24rpx;
  background-color: #adb3b5;
  opacity: 0.2;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24rpx;
  max-width: 768rpx;
  margin: 0 auto;
  width: 100%;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300rpx;
  gap: 16rpx;
  color: #5a6062;
}

.welcome-text {
  font-size: 40rpx;
  font-weight: 700;
}

.welcome-subtitle {
  font-size: 24rpx;
  color: #adb3b5;
}

.message-wrapper {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 16rpx;

  &--user {
    justify-content: flex-end;
  }
}

.hunch-wrapper {
  margin: 24rpx 0;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx;
}

.loading-dot {
  font-size: 20rpx;
  color: #006c5a;
  animation: bounce 1.4s ease-in-out infinite;

  &:nth-child(2) {
    animation-delay: 0.2s;
  }

  &:nth-child(3) {
    animation-delay: 0.4s;
  }
}

@keyframes bounce {
  0%,
  100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-10rpx);
  }
}

.input-area {
  position: fixed;
  bottom: 100rpx;
  left: 24rpx;
  right: 24rpx;
  display: flex;
  gap: 12rpx;
  max-width: 720rpx;
  margin: 0 auto;
  z-index: 40;
}

.input-wrapper {
  flex: 1;
  background-color: #f1f4f5;
  border-radius: 16rpx;
  overflow: hidden;
  display: flex;
}

.user-input {
  flex: 1;
  padding: 16rpx 24rpx;
  border: none;
  background: transparent;
  font-size: 24rpx;
  color: #2d3335;

  &::placeholder {
    color: #adb3b5;
  }
}

.submit-btn {
  width: 56rpx;
  height: 56rpx;
  border: none;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #006c5a 0%, #7ae8cc 100%);
  color: #e4fff5;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  &:disabled {
    opacity: 0.6;
  }
}

.game-footer {
  position: fixed;
  bottom: 80rpx;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 20rpx;
  color: #5a6062;
  padding: 8rpx;
}
</style>
