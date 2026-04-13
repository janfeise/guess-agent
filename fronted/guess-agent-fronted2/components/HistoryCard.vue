<template>
  <div class="history-card" @click="handleClick">
    <div class="history-card__header">
      <div class="history-card__info">
        <text class="history-card__date">{{ formattedDate }}</text>
        <text class="history-card__word">{{ word }}</text>
        <div class="history-card__tags">
          <span class="tag" :class="`tag--${result}`">{{ resultLabel }}</span>
          <span class="tag tag--difficulty">{{ difficultyLabel }}</span>
        </div>
      </div>
      <div class="history-card__arrow">›</div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from "vue";
import { DIFFICULTY_LABELS, RESULT_LABELS } from "../utils/constants";

const props = defineProps({
  word: {
    type: String,
    required: true,
  },
  result: {
    type: Boolean, // true = won, false = lost
    required: true,
  },
  difficulty: {
    type: String,
    required: true,
  },
  timestamp: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["click"]);

const formattedDate = computed(() => {
  const date = new Date(props.timestamp);
  return date.toLocaleDateString("zh-CN");
});

const resultLabel = computed(() => {
  return props.result ? RESULT_LABELS.won : RESULT_LABELS.lost;
});

const difficultyLabel = computed(() => {
  return DIFFICULTY_LABELS[props.difficulty] || props.difficulty;
});

const handleClick = () => {
  emit("click");
};
</script>

<style scoped lang="scss">
.history-card {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 12rpx 40rpx rgba(45, 51, 53, 0.06);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

  &:active {
    transform: translateY(-4rpx);
  }

  &__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  &__info {
    display: flex;
    flex-direction: column;
    gap: 8rpx;
    flex: 1;
  }

  &__date {
    font-size: 20rpx;
    color: #5a6062;
    text-transform: uppercase;
    letter-spacing: 1rpx;
    font-weight: 600;
    opacity: 0.6;
  }

  &__word {
    font-size: 40rpx;
    color: #2d3335;
    font-weight: 700;
    font-family: "Plus Jakarta Sans", sans-serif;
    display: block;
    letter-spacing: 2rpx;
  }

  &__tags {
    display: flex;
    gap: 12rpx;
    margin-top: 8rpx;
  }

  &__arrow {
    font-size: 28rpx;
    color: #006c5a;
    width: 48rpx;
    height: 48rpx;
    border-radius: 16rpx;
    background-color: #f1f4f5;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .tag {
    display: inline-flex;
    align-items: center;
    padding: 8rpx 12rpx;
    border-radius: 24rpx;
    font-size: 20rpx;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2rpx;

    &--won {
      background-color: #89f6da;
      color: #005d4d;
    }

    &--lost {
      background-color: #fa746f;
      color: #6e0a12;
    }

    &--difficulty {
      background-color: #ebeef0;
      color: #5a6062;
    }
  }
}
</style>
