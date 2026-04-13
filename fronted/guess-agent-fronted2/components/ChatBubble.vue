<template>
  <div class="chat-bubble" :class="[`chat-bubble--${type}`]">
    <div v-if="type === 'agent'" class="chat-bubble__label">
      <text class="label-text">空灵向导</text>
      <text class="label-icon">✨</text>
    </div>
    <div class="chat-bubble__content">
      <text>{{ message }}</text>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: "agent", // 'agent' or 'user'
    validator: (value) => ["agent", "user"].includes(value),
  },
});
</script>

<style scoped lang="scss">
.chat-bubble {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: 24rpx;

  &--agent {
    align-items: flex-start;
    max-width: 85%;

    .chat-bubble__content {
      background-color: #feec95;
      color: #63570f;
      border-radius: 16rpx 16rpx 16rpx 0;
      box-shadow: 0 4rpx 20rpx rgba(45, 51, 53, 0.04);
      padding: 20rpx;
    }
  }

  &--user {
    align-items: flex-end;
    max-width: 80%;

    .chat-bubble__content {
      background-color: #dee3e6;
      color: #2d3335;
      border-radius: 16rpx 16rpx 0 16rpx;
      box-shadow: 0 4rpx 20rpx rgba(45, 51, 53, 0.04);
      padding: 20rpx;
    }
  }

  &__label {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 22rpx;
    color: #5a6062;
    font-weight: 700;
    margin: 0 4rpx;
  }

  &__content {
    font-size: 28rpx;
    line-height: 1.5;
    word-wrap: break-word;
  }

  .label-text {
    font-size: 20rpx;
    text-transform: uppercase;
    letter-spacing: 1rpx;
  }

  .label-icon {
    font-size: 24rpx;
  }
}
</style>
