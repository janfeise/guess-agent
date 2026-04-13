<template>
  <nav class="bottom-nav">
    <a
      v-for="item in items"
      :key="item.pagePath"
      class="bottom-nav__item"
      :class="{ 'bottom-nav__item--active': isActive(item.pagePath) }"
      @click="handleNavigate(item.pagePath)"
    >
      <text class="bottom-nav__icon">{{ item.icon }}</text>
      <text class="bottom-nav__text">{{ item.text }}</text>
    </a>
  </nav>
</template>

<script setup>
import { ref, defineProps } from "vue";

const props = defineProps({
  items: {
    type: Array,
    default: () => [
      { text: "首页", pagePath: "pages/index/index", icon: "🏠" },
      { text: "历史", pagePath: "pages/history/history", icon: "⏱️" },
      { text: "规则", pagePath: "pages/rules/rules", icon: "📖" },
    ],
  },
});

const getCurrentPagePath = () => {
  const pages = uni.getCurrentPages();
  if (pages.length === 0) return "";
  const currentPage = pages[pages.length - 1];
  return currentPage.route || "";
};

const isActive = (pagePath) => {
  const currentPath = getCurrentPagePath();
  return currentPath === pagePath;
};

const handleNavigate = (pagePath) => {
  uni.switchTab({
    url: "/" + pagePath,
  });
};
</script>

<style scoped lang="scss">
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  background-color: #f8f9fa;
  border-top: 1rpx solid rgba(5, 150, 105, 0.1);
  padding: 12rpx 12rpx 24rpx 12rpx;
  box-shadow: 0 -12rpx 40rpx rgba(45, 51, 53, 0.06);

  &__item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12rpx 20rpx;
    color: #5a6062;
    text-decoration: none;
    font-size: 0;
    transition: all 0.3s ease;

    &--active {
      background-color: rgba(5, 150, 105, 0.1);
      color: #006c5a;
      border-radius: 24rpx;
      transform: translateY(-4rpx);
    }
  }

  &__icon {
    font-size: 32rpx;
    margin-bottom: 8rpx;
    display: block;
  }

  &__text {
    font-size: 20rpx;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1rpx;
  }
}
</style>
