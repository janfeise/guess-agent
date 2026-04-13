<template>
  <div class="result-card">
    <div class="result-card__icon">{{ icon }}</div>
    <div class="result-card__content">
      <text class="result-card__label">{{ label }}</text>
      <text class="result-card__value">{{ value }}</text>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";

defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  icon: {
    type: String,
    required: true,
  },
});
</script>

<style scoped lang="scss">
.result-card {
  background-color: #f1f4f5;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160rpx;

  &__icon {
    font-size: 40rpx;
    margin-bottom: 16rpx;
  }

  &__label {
    font-size: 20rpx;
    color: #5a6062;
    text-transform: uppercase;
    letter-spacing: 2rpx;
    font-weight: 600;
    display: block;
    margin-bottom: 8rpx;
  }

  &__value {
    font-size: 40rpx;
    color: #2d3335;
    font-weight: 700;
    display: block;
    font-family: "Plus Jakarta Sans", sans-serif;
  }
}
</style>
