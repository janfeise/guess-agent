<template>
  <view class="history-page">
    <TopBar />

    <view class="history-page__container">
      <view class="page-header">
        <text class="page-title">对局历史</text>
        <text class="page-subtitle"
          >记录您在直觉档案中，与空灵向导的精彩旅程。</text
        >
      </view>

      <FilterTab v-model="activeFilter" @change="handleFilterChange" />

      <view v-if="filteredGames.length > 0" class="history-list">
        <view
          v-for="game in filteredGames"
          :key="game.gameId"
          @click="handleGameClick(game)"
        >
          <HistoryCard
            :word="game.startWord"
            :result="game.isWon"
            :difficulty="game.difficulty"
            :timestamp="game.timestamp"
          />
        </view>
      </view>

      <view v-else class="empty-state">
        <text class="empty-state__icon">📭</text>
        <text class="empty-state__text">暂无游戏记录</text>
        <button class="btn-start" @click="handleStartGame">开始游戏</button>
      </view>

      <!-- Statistics Section -->
      <view v-if="stats.totalGames > 0" class="stats-section">
        <view class="stats-title">📊 你的成绩统计</view>
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-value">{{ stats.totalGames }}</text>
            <text class="stat-label">总局数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.winsCount }}</text>
            <text class="stat-label">胜场</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ winRate }}%</text>
            <text class="stat-label">胜率</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.minRounds || "-" }}</text>
            <text class="stat-label">最少轮数</text>
          </view>
        </view>
      </view>
    </view>

    <BottomNav />
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import TopBar from "../../components/TopBar.vue";
import BottomNav from "../../components/BottomNav.vue";
import FilterTab from "../../components/FilterTab.vue";
import HistoryCard from "../../components/HistoryCard.vue";
import { getGameHistory, getUserStats } from "../../utils/storage";

const activeFilter = ref("all");
const allGames = ref([]);
const stats = ref({
  totalGames: 0,
  winsCount: 0,
  lossesCount: 0,
  minRounds: null,
});

const filteredGames = computed(() => {
  if (activeFilter.value === "all") {
    return allGames.value;
  } else if (activeFilter.value === "won") {
    return allGames.value.filter((g) => g.isWon);
  } else if (activeFilter.value === "lost") {
    return allGames.value.filter((g) => !g.isWon);
  }
  return allGames.value;
});

const winRate = computed(() => {
  if (stats.value.totalGames === 0) return 0;
  return Math.round((stats.value.winsCount / stats.value.totalGames) * 100);
});

const handleFilterChange = (filter) => {
  activeFilter.value = filter;
};

const handleGameClick = (game) => {
  uni.navigateTo({
    url: "/pages/result/result",
    success: () => {
      const pages = getCurrentPages();
      const resultPage = pages[pages.length - 1];
      resultPage.showGameResult(game);
    },
  });
};

const handleStartGame = () => {
  uni.switchTab({
    url: "/pages/index/index",
  });
};

const loadData = () => {
  const history = getGameHistory();
  allGames.value = history;

  const userStats = getUserStats();
  stats.value = userStats;
};

onMounted(() => {
  loadData();
});
</script>

<style scoped lang="scss">
.history-page {
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

.page-header {
  margin-bottom: 32rpx;
}

.page-title {
  display: block;
  font-size: 40rpx;
  font-weight: 900;
  color: #2d3335;
  margin-bottom: 8rpx;
  font-family: "Plus Jakarta Sans", sans-serif;
  letter-spacing: 1rpx;
}

.page-subtitle {
  display: block;
  font-size: 24rpx;
  color: #5a6062;
  line-height: 1.5;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.empty-state {
  text-align: center;
  padding: 80rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;

  &__icon {
    font-size: 80rpx;
    opacity: 0.5;
  }

  &__text {
    font-size: 28rpx;
    color: #5a6062;
    margin-bottom: 16rpx;
  }
}

.btn-start {
  padding: 16rpx 32rpx;
  border: none;
  border-radius: 16rpx;
  background-color: #006c5a;
  color: #e4fff5;
  font-size: 24rpx;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
  }
}

.stats-section {
  margin-top: 48rpx;
  background-color: rgba(137, 246, 218, 0.1);
  border-radius: 16rpx;
  padding: 24rpx;
}

.stats-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #2d3335;
  margin-bottom: 24rpx;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.stat-item {
  text-align: center;
  padding: 16rpx;
  background-color: #ffffff;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.stat-value {
  display: block;
  font-size: 32rpx;
  font-weight: 900;
  color: #006c5a;
  font-family: "Plus Jakarta Sans", sans-serif;
}

.stat-label {
  display: block;
  font-size: 20rpx;
  color: #5a6062;
  text-transform: uppercase;
  letter-spacing: 1rpx;
}
</style>
