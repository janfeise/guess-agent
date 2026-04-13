<template>
  <header class="top-bar">
    <div class="top-bar__content">
      <button class="top-bar__menu" @click="handleMenuClick">
        <text class="icon">☰</text>
      </button>
      <h1 class="top-bar__title">Guess Agent</h1>
    </div>
  </header>
</template>

<script setup>
import { defineProps, defineEmits } from "vue";

const emit = defineEmits(["menu-click"]);

const handleMenuClick = () => {
  emit("menu-click");
};
</script>

<style scoped lang="scss">
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: linear-gradient(to bottom, #f8f9fa, rgba(248, 249, 250, 0));
  backdrop-filter: blur(20px);
  padding-top: var(--status-bar-height, 0);
  width: 100%;

  &__content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16rpx 24rpx;
    max-width: 1280rpx;
    margin: 0 auto;
    width: 100%;
  }

  &__menu {
    padding: 0;
    margin: 0;
    border: none;
    background: none;
    font-size: 28rpx;
    color: #059669;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40rpx;
    height: 40rpx;
    border-radius: 50%;
    transition: all 0.3s ease;

    &:active {
      opacity: 0.7;
      transform: scale(0.95);
    }
  }

  &__title {
    font-size: 32rpx;
    font-weight: 900;
    color: #065f46;
    margin: 0;
    letter-spacing: 2rpx;
    font-family: "Plus Jakarta Sans", sans-serif;
  }

  &__avatar {
    width: 40rpx;
    height: 40rpx;
    border-radius: 50%;
    border: 2rpx solid #d1fae5;
    display: block;
    object-fit: cover;
  }
}
</style>
