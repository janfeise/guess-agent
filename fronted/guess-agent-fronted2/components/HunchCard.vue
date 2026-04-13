<template>
  <div class="hunch-card">
    <div class="hunch-card__header">
      <text class="hunch-card__icon">💡</text>
      <text class="hunch-card__title">助手直觉</text>
    </div>
    <text class="hunch-card__hint">{{ hintText }}</text>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  hintText: {
    type: String,
    required: true,
  },
});
</script>

<style scoped lang="scss">
.hunch-card {
  background: rgba(222, 227, 230, 0.4);
  backdrop-filter: blur(20px);
  border-radius: 16rpx;
  padding: 24rpx;
  margin: 16rpx 0;
  border: 1rpx solid rgba(255, 255, 255, 0.2);

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 16rpx;
  }

  &__icon {
    font-size: 24rpx;
  }

  &__title {
    font-size: 20rpx;
    font-weight: 700;
    color: #2d3335;
    text-transform: uppercase;
    letter-spacing: 2rpx;
  }

  &__hint {
    font-size: 28rpx;
    color: #2d3335;
    font-weight: 600;
    line-height: 1.6;
    display: block;
    font-style: italic;
  }
}
</style>
