<template>
  <view class="rules-page">
    <TopBar />

    <view class="rules-page__container">
      <!-- Hero Section -->
      <view class="hero">
        <view class="hero__badge">操作指南</view>
        <text class="hero__title"
          >掌握猜词的 <text class="italic">艺术</text>。</text
        >
        <text class="hero__subtitle">
          空灵向导正在等候。学会穿梭于语言迷宫，赢取属于你的胜利。
        </text>
      </view>

      <!-- Three Phases -->
      <view class="phases">
        <view class="phase-card">
          <view class="phase-icon">💬</view>
          <text class="phase-title">提问</text>
          <text class="phase-desc">
            用巧妙的问题询问 AI。尝试在不直接点破的情况下缩小概念范围。
          </text>
        </view>

        <view class="phase-card">
          <view class="phase-icon">💡</view>
          <text class="phase-title">推测</text>
          <text class="phase-desc">
            当你确信时输入你的"直觉"。每一次错误的猜测都会增加挑战难度。
          </text>
        </view>

        <view class="phase-card">
          <view class="phase-icon">✅</view>
          <text class="phase-title">确认</text>
          <text class="phase-desc">
            向导将揭示真相。根据你的速度和精准度进行评分。
          </text>
        </view>
      </view>

      <!-- Game Rules -->
      <view class="rules-section">
        <view class="section-title">📖 游戏规则</view>

        <view class="rule-item">
          <view class="rule-number">01</view>
          <view class="rule-content">
            <text class="rule-heading">提问限制</text>
            <text class="rule-text"
              >每局你只有 10
              个提问名额（难度不同）。请谨慎使用，向导的回答非常精简。</text
            >
          </view>
        </view>

        <view class="rule-item">
          <view class="rule-number">02</view>
          <view class="rule-content">
            <text class="rule-heading">禁止专有名词</text>
            <text class="rule-text"
              >问题必须是概念性的。禁止询问具体姓名或特定地点。</text
            >
          </view>
        </view>

        <view class="rule-item">
          <view class="rule-number">03</view>
          <view class="rule-content">
            <text class="rule-heading">最终推测</text>
            <text class="rule-text"
              >在游戏结束和谜题揭晓前，你只有 3 次猜测机会（难度不同）。</text
            >
          </view>
        </view>

        <view class="rule-item">
          <view class="rule-number">04</view>
          <view class="rule-content">
            <text class="rule-heading">计分方式</text>
            <text class="rule-text"
              >根据轮数、时间和 AI
              信心指数综合评分。速度快、精准度高的玩法得分更高。</text
            >
          </view>
        </view>
      </view>

      <!-- Hunch Explanation -->
      <view class="hunch-section">
        <view class="hunch-title">🎯 "直觉（Hunch）"提示是什么？</view>
        <text class="hunch-text">
          在你提问时，AI
          助手会偶尔给出一个神秘的"直觉"提示。这不是答案，而是一个线索，帮助你重新思考这个词的特征或用途。直觉卡片使用隐喻和诗意的语言，考验你的联想能力。
        </text>
        <view class="hint-example">
          <text class="hint-label">例子：</text>
          <text class="hint-content"
            >"我是微风的无声伙伴，却能承载天空的泪滴。"</text
          >
          <text class="hint-answer">（答案：雨伞）</text>
        </view>
      </view>

      <!-- Tips -->
      <view class="tips-section">
        <view class="tips-title">💡 小贴士</view>
        <view class="tips-list">
          <view class="tip-item">
            <text class="tip-icon">✓</text>
            <text class="tip-text">从广泛的方向开始，然后逐步缩小范围</text>
          </view>
          <view class="tip-item">
            <text class="tip-icon">✓</text>
            <text class="tip-text">注意 AI 的措辞，有时会暗示答案的性质</text>
          </view>
          <view class="tip-item">
            <text class="tip-icon">✓</text>
            <text class="tip-text">充分利用"直觉"提示中的隐喻和象征</text>
          </view>
          <view class="tip-item">
            <text class="tip-icon">✓</text>
            <text class="tip-text">不要急于猜测，充分利用你的提问机会</text>
          </view>
        </view>
      </view>

      <!-- Start Button -->
      <view class="start-section">
        <button class="btn-play" @click="handleStartGame">开始挑战 🚀</button>
      </view>
    </view>

    <BottomNav />
  </view>
</template>

<script setup>
import TopBar from "../../components/TopBar.vue";
import BottomNav from "../../components/BottomNav.vue";

const handleStartGame = () => {
  uni.switchTab({
    url: "/pages/index/index",
  });
};
</script>

<style scoped lang="scss">
.rules-page {
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

.hero {
  text-align: center;
  margin-bottom: 48rpx;

  &__badge {
    display: inline-block;
    background-color: #89f6da;
    color: #005d4d;
    padding: 8rpx 16rpx;
    border-radius: 24rpx;
    font-size: 20rpx;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2rpx;
    margin-bottom: 16rpx;
  }

  &__title {
    display: block;
    font-size: 40rpx;
    font-weight: 900;
    color: #2d3335;
    margin-bottom: 16rpx;
    line-height: 1.2;
    font-family: "Plus Jakarta Sans", sans-serif;

    .italic {
      color: #006c5a;
      font-style: italic;
    }
  }

  &__subtitle {
    display: block;
    font-size: 24rpx;
    color: #5a6062;
    line-height: 1.6;
  }
}

.phases {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16rpx;
  margin-bottom: 48rpx;
}

.phase-card {
  background-color: #f1f4f5;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: left;
  transition: all 0.3s ease;

  &:active {
    background-color: #ebeef0;
  }
}

.phase-icon {
  font-size: 40rpx;
  margin-bottom: 12rpx;
}

.phase-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 8rpx;
}

.phase-desc {
  display: block;
  font-size: 22rpx;
  color: #5a6062;
  line-height: 1.5;
}

.rules-section {
  margin-bottom: 48rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 24rpx;
}

.rule-item {
  display: flex;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

.rule-number {
  font-size: 32rpx;
  font-weight: 900;
  color: #006c5a;
  opacity: 0.2;
  min-width: 40rpx;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.rule-content {
  flex: 1;
}

.rule-heading {
  display: block;
  font-size: 24rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 8rpx;
}

.rule-text {
  display: block;
  font-size: 20rpx;
  color: #5a6062;
  line-height: 1.6;
}

.hunch-section {
  background-color: rgba(222, 227, 230, 0.4);
  backdrop-filter: blur(20px);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.hunch-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 16rpx;
}

.hunch-text {
  display: block;
  font-size: 22rpx;
  color: #2d3335;
  line-height: 1.6;
  margin-bottom: 16rpx;
}

.hint-example {
  background-color: #ffffff;
  border-radius: 12rpx;
  padding: 16rpx;
  margin-top: 12rpx;
}

.hint-label {
  display: block;
  font-size: 18rpx;
  color: #5a6062;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  margin-bottom: 8rpx;
  font-weight: 600;
}

.hint-content {
  display: block;
  font-size: 22rpx;
  color: #2d3335;
  font-style: italic;
  margin-bottom: 8rpx;
}

.hint-answer {
  display: block;
  font-size: 18rpx;
  color: #006c5a;
  font-weight: 600;
  margin-top: 8rpx;
}

.tips-section {
  margin-bottom: 48rpx;
}

.tips-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 24rpx;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 16rpx;
  background-color: #ffffff;
  border-radius: 12rpx;
  border-left: 4rpx solid #006c5a;
}

.tip-icon {
  font-size: 24rpx;
  color: #006c5a;
  font-weight: 700;
  min-width: 24rpx;
  margin-top: 2rpx;
}

.tip-text {
  display: block;
  font-size: 22rpx;
  color: #2d3335;
  line-height: 1.5;
}

.start-section {
  display: flex;
  justify-content: center;
  padding: 24rpx 0;
}

.btn-play {
  width: 100%;
  padding: 20rpx;
  border: none;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #006c5a 0%, #7ae8cc 100%);
  color: #e4fff5;
  font-size: 28rpx;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 108, 90, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
  }
}
</style>
