<template>
  <div class="filter-tabs">
    <button
      v-for="item in filters"
      :key="item.value"
      class="filter-btn"
      :class="{ 'filter-btn--active': activeFilter === item.value }"
      @click="handleFilterChange(item.value)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref } from "vue";

const props = defineProps({
  filters: {
    type: Array,
    default: () => [
      { label: "全部", value: "all" },
      { label: "获胜", value: "won" },
      { label: "落败", value: "lost" },
    ],
  },
  modelValue: {
    type: String,
    default: "all",
  },
});

const emit = defineEmits(["update:modelValue", "change"]);

const activeFilter = ref(props.modelValue);

const handleFilterChange = (value) => {
  activeFilter.value = value;
  emit("update:modelValue", value);
  emit("change", value);
};
</script>

<style scoped lang="scss">
.filter-tabs {
  display: flex;
  gap: 12rpx;
  overflow-x: auto;
  padding-bottom: 8rpx;
  margin-bottom: 24rpx;

  &::-webkit-scrollbar {
    display: none;
  }
}

.filter-btn {
  flex-shrink: 0;
  padding: 12rpx 24rpx;
  border-radius: 24rpx;
  border: none;
  font-size: 24rpx;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1rpx;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;

  &--active {
    background-color: #006c5a;
    color: #e4fff5;
  }

  &:not(&--active) {
    background-color: #e5e9eb;
    color: #5a6062;

    &:active {
      opacity: 0.8;
    }
  }
}
</style>
