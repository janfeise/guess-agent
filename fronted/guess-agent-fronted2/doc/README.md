# 🎮 HUNCH - AI 单词游戏 | uni-app 完整项目

> 基于 Google Stitch 原型重构的完整 uni-app 项目，包含完整交互逻辑、组件系统、游戏引擎和本地数据持久化

## ✨ 项目亮点

✅ **完整的游戏流程** - 从首页→游戏进行→成绩展示，逻辑完善  
✅ **AI交互系统** - 模拟AI思考延迟、生成响应、Hunch直觉提示  
✅ **多难度配置** - 简单/普通/困难，动态调整参数  
✅ **本地数据持久化** - 游戏历史、用户统计、成绩分析  
✅ **7个可复用组件** - TopBar、ChatBubble、HunchCard 等  
✅ **完整交互反馈** - Toast、Loading、动画、自动滚动  
✅ **Material Design 3** - 完整的设计系统和原型还原  
✅ **响应式布局** - Bento Grid + 适配各种屏幕

---

## 📂 项目结构

```
guess-agent-fronted/
├── pages/
│   ├── index/          # 🏠 首页 - 游戏开始（Bento Layout）
│   ├── gamePlay/       # 🎮 游戏进行页 - 核心交互
│   ├── result/         # 🏆 结果页 - 成绩展示
│   ├── history/        # 📋 历史记录页 - 数据管理
│   └── rules/          # 📖 规则说明页 - 帮助文档
│
├── components/
│   ├── TopBar.vue      # 顶部导航栏（固定+毛玻璃）
│   ├── ChatBubble.vue  # 聊天气泡（AI/用户区分）
│   ├── HunchCard.vue   # AI提示卡片
│   ├── ResultCard.vue  # 统计卡片
│   ├── HistoryCard.vue # 历史记录卡片
│   ├── FilterTab.vue   # 筛选标签组
│   └── BottomNav.vue   # 底部导航栏
│
├── utils/
│   ├── gameLogic.js    # 游戏核心逻辑（难度、AI、计分）
│   ├── storage.js      # 本地存储（历史、统计）
│   └── constants.js    # 全局常量（颜色、消息）
│
├── doc/
│   ├── 完整项目文档.md  # 详细功能说明
│   ├── 快速参考.md     # 快速查询指南
│   ├── 架构设计.md     # 系统架构详解
│   ├── 交互设计说明.md # 所有交互流程
│   └── README.md       # 本文档
│
├── pages.json          # 页面配置 + Tab栏
├── App.vue             # 应用入口
├── main.js             # 主程序
└── manifest.json       # 应用清单
```

└── manifest.json # 应用清单

```

---

## 🎯 核心功能

### 1️⃣ 游戏开始流程

```

输入单词 "自行车" + 选择难度 "普通"
↓
点击"开始游戏"
↓
创建游戏对象 (10问题名额, 3猜测次数)
↓
跳转到游戏进行页
↓
AI初始化消息: "我已经想到一个词..."

```

### 2️⃣ 游戏进行交互

```

用户输入: "它是生物吗?"
↓
系统判断输入类型: 问题 ✓
↓
AI生成回答: "取决于物体的特性..." (延迟800-2000ms)
↓
轮次+1, 问题数+1
↓
每3次提问显示 Hunch 提示: "多考虑依靠人力的工具..."
↓
用户猜测: "自行车"
↓
判断正确/错误 → 胜利/失败

```

### 3️⃣ 结果展示

```

胜利: ✅ 展示答案 + 用时 + 轮次 + AI信心指数
失败: ❌ 展示答案 + 尝试次数

可选操作:
├─ 再玩一次 → 返回首页重新开始
└─ 返回首页 → 查看历史记录

```

### 4️⃣ 历史管理

```

查看所有历史记录
├─ 筛选: 全部 / 获胜 / 落败
└─ 展示统计: 总局数 / 胜率 / 最佳成绩

点击历史记录
└─ 查看该局详细结果

````

---

## 💻 技术栈

| 技术     | 说明                              |
| -------- | --------------------------------- |
| **框架** | uni-app (Vue 3 + Composition API) |
| **样式** | SCSS (支持 rpx 响应式像素)        |
| **存储** | uni.storage (本地持久化)          |
| **路由** | uni-app 内置路由                  |
| **UI**   | Material Design 3 设计系统        |

---

## 🚀 快速开始

### 环境要求

- Node.js ≥ 12.0
- HBuilderX 或支持 uni-app 的 IDE
- 微信开发者工具 (可选，用于调试)

### 安装步骤

```bash
# 1. 进入项目目录
cd guess-agent-fronted

# 2. 安装依赖 (如果有 package.json)
npm install

# 3. 开发模式运行
npm run dev

# 4. 编译发布
# 使用 HBuilderX：项目右键 → 发行 → 选择平台
````

### 在 HBuilderX 中运行

```
1. 打开项目
2. 点击顶部菜单: 运行 → 运行到浏览器
3. 或下载 uni-app 插件后在手机上实时预览
```

---

## 📖 文档导航

| 文档                                  | 用途                                    |
| ------------------------------------- | --------------------------------------- |
| [完整项目文档](./doc/完整项目文档.md) | **深入了解** - 详细功能、组件、工具函数 |
| [快速参考](./doc/快速参考.md)         | **快速查询** - 常用操作、代码示例       |
| [架构设计](./doc/架构设计.md)         | **系统级** - 架构图、数据流、扩展点     |
| [交互设计说明](./doc/交互设计说明.md) | **交互细节** - 所有交互流程、反馈机制   |

---

## 🎮 游戏规则

### 难度配置

| 难度等级 | 提问名额 | 猜测次数 | 适合人群 |
| -------- | -------- | -------- | -------- |
| 🟢 简单  | 15       | 5        | 新手入门 |
| 🔵 普通  | 10       | 3        | 标准难度 |
| 🔴 困难  | 7        | 2        | 高手挑战 |

### 游戏玩法

1. **提问** - 问AI概念性问题，消耗提问名额
2. **获得提示** - 每3次提问后AI给出神秘的"直觉"提示
3. **猜测** - 输入目标词语，消耗猜测次数
4. **判决** - 猜对赢，猜错继续或失败

---

## 📊 数据结构

### 游戏对象

```javascript
{
  id: "game_1234567890_abc123",
  startWord: "自行车",
  difficulty: "medium",
  questionsUsed: 8,
  questionLimit: 10,
  guessesUsed: 1,
  guessLimit: 3,
  roundNum: 12,
  status: "playing",    // playing/won/lost
  messages: [...],      // 聊天记录
  startTime: 1234567890
}
```

### 结果对象

```javascript
{
  gameId: "game_...",
  startWord: "自行车",
  finalAnswer: "BICYCLE",
  isWon: true,
  roundsUsed: 12,
  questionsUsed: 8,
  guessesUsed: 1,
  totalTime: 270000,      // 毫秒
  aiConfidence: 85,       // 百分比
  timestamp: 1234567890
}
```

### 用户统计

```javascript
{
  totalGames: 15,
  winsCount: 9,
  lossesCount: 6,
  byDifficulty: {
    easy: { played: 5, won: 5 },
    medium: { played: 7, won: 3 },
    hard: { played: 3, won: 1 }
  },
  bestTime: 120000,
  minRounds: 4,
  lastPlayTime: 1234567890
}
```

---

## 🎨 设计系统

### 颜色规范

```
🟢 主色   (Primary)     #006c5a  深翠绿
💚 浅色   (Light)       #89f6da  薄荷绿
💛 强调色 (Tertiary)    #feec95  金黄 (AI提示)
🩶 文字   (Text)        #2d3335  深灰
```

### 排版

```
标题: Plus Jakarta Sans, 40-72rpx, 900粗
正文: Inter, 24-28rpx, 400-600
```

### 动画时长

```
按钮:   200ms
过渡:   300ms
滚动:   300ms
```

---

## 🔧 主要 API

### gameLogic.js

```javascript
createNewGame(word, difficulty)        // 创建游戏
detectInputType(input)                // 判断提问/猜测
generateAIResponse(roundNum, diff)    // 生成AI回答
generateHunchHint(word)               // 生成直觉提示
calculateAIConfidence(...)            // 计算AI信心指数
createGameResult(game, answer, isWon) // 生成结果
```

### storage.js

```javascript
saveGameResult(result); // 保存游戏结果
getGameHistory(filter); // 获取历史记录
getUserStats(); // 获取用户统计
getWinRate(); // 获取胜率
clearGameHistory(); // 清除历史记录
```

---

## 🧪 测试清单

- [x] 首页表单验证
- [x] 游戏流程（提问→Hunch→猜测→结束）
- [x] 限制检查（名额用完）
- [x] 本地存储（历史、统计）
- [x] 页面导航和数据传递
- [x] 列表筛选
- [x] 动画和过渡效果

---

## 📝 文件清单

### 已生成文件

```
✅ pages/
   ✅ index/index.vue        (600+ 行)
   ✅ gamePlay/gamePlay.vue  (500+ 行)
   ✅ result/result.vue      (400+ 行)
   ✅ history/history.vue    (400+ 行)
   ✅ rules/rules.vue        (600+ 行)

✅ components/
   ✅ TopBar.vue            (100+ 行)
   ✅ ChatBubble.vue        (80+ 行)
   ✅ HunchCard.vue         (70+ 行)
   ✅ ResultCard.vue        (70+ 行)
   ✅ HistoryCard.vue       (120+ 行)
   ✅ FilterTab.vue         (90+ 行)
   ✅ BottomNav.vue         (110+ 行)

✅ utils/
   ✅ gameLogic.js          (250+ 行)
   ✅ storage.js            (200+ 行)
   ✅ constants.js          (100+ 行)

✅ doc/
   ✅ 完整项目文档.md        (600+ 行)
   ✅ 快速参考.md           (300+ 行)
   ✅ 架构设计.md           (500+ 行)
   ✅ 交互设计说明.md        (500+ 行)

✅ pages.json              (页面 + Tab配置)
```

**总代码行数**: 4500+ 行

---

## 🚀 扩展建议

### 短期 (v1.1)

- [ ] 深色主题支持
- [ ] 更多AI提示库
- [ ] 自定义题库
- [ ] 分享成绩功能

### 中期 (v2.0)

- [ ] 真实AI后端集成
- [ ] 用户账号系统
- [ ] 排行榜功能
- [ ] 多人对战模式

### 长期 (v3.0)

- [ ] 成就系统
- [ ] 每日挑战
- [ ] 社交分享
- [ ] 深度学习推荐

---

## 📞 常见问题

**Q: 如何重置所有数据？**

```javascript
import { clearAllData } from "@/utils/storage";
clearAllData();
```

**Q: 如何修改AI回答？**  
编辑 `utils/gameLogic.js` 中的 `generateAIResponse()` 函数

**Q: 如何调整难度参数？**  
修改 `utils/gameLogic.js` 中的 `DIFFICULTY_LEVELS` 对象

**Q: 如何导出游戏历史？**

```javascript
const history = getGameHistory();
const json = JSON.stringify(history);
// 保存 json 到文件
```

---

## 📄 许可证

本项目基于 Google Stitch 原型进行创意重构。  
代码遵循 MIT 许可证。

---

## 👨‍💻 开发者信息

**项目名称**: HUNCH - AI 单词游戏  
**框架**: uni-app (Vue 3)  
**设计系统**: Material Design 3  
**最后更新**: 2026年4月13日  
**版本**: 1.0.0

---

## 🎉 开始开发！

```bash
npm run dev
# 或在 HBuilderX 中打开项目运行
```

**祝你开发愉快！** 🚀  
如有问题，请参考 [完整项目文档](./doc/完整项目文档.md) 获取更多帮助。
