# 猜词 Agent 项目文档

## 项目背景

大语言模型正在从工具演变为“参与者”，不仅能回答问题，还能参与规则明确的互动场景。在娱乐与学习融合的方向中，引入 Agent 参与对抗式游戏，是一种更具沉浸感的实践方式

“学科猜词大挑战”基于这一思路设计，通过将 LLM、加密机制与回合制规则结合，构建一个既具策略性又具知识性的交互系统。同时引入“用户侧小助手”，强化学习辅助能力，而不干扰游戏公平性

------

## 项目目标

构建一个以 Agent 为核心的猜词系统，实现以下能力：

- 支持用户 vs Agent 的对抗式猜词玩法
- 支持学科类词库（计算机、数学、历史等）
- 引入加密机制，确保答案不可见
- 提供用户侧“小助手”，用于查询与推理辅助
- 提供记录面板，支持推理过程记录与复盘
- 支持上下文驱动的多轮对话推理

------

## 核心玩法设计

### 游戏流程

1. 用户输入答案 + 自定义密钥
2. 系统生成 Agent 答案（内部自动设定密钥）
3. 双方答案统一加密，仅存储密文
4. 进入回合制问答：
	- 用户提问（是/否问题）
	- Agent 基于上下文进行推理回答
5. 用户可随时使用“小助手”进行查询与辅助推理
6. 用户进行猜测
7. 系统进行密文校验
8. 游戏结束后输入密钥进行解密验证

------

### 规则约束

- 严格轮流机制（单轮单问）
- Agent 不可直接暴露答案
- 小助手不参与答案推理，仅提供知识支持
- 所有答案在游戏过程中始终以密文存在

------

## 系统架构设计（重构）

系统拆分为四个核心模块：

### Agent 模块（核心控制层）

职责：

- 控制游戏流程与轮次
- 管理上下文（历史问答）
- 调用 LLM 进行推理
- 判断用户猜测是否命中

------

### 加密模块（安全层）

职责：

- 用户答案加密
- Agent 答案加密
- 游戏结束后解密验证

示例（Python）：

```python
from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key(password: str):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt(text: str, password: str):
    key = generate_key(password)
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

def decrypt(token: str, password: str):
    key = generate_key(password)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()
```

------

### 小助手模块（用户侧工具）

定位：**完全服务用户，不参与游戏规则**

职责：

- 提供知识查询（如：某概念属于哪个领域）
- 提供提问建议（优化猜词策略）
- 根据历史记录给出推理提示

关键约束：

- 不访问密文答案
- 不参与 Agent 推理
- 不影响胜负判定

------

### 数据模块（持久化层）

使用 MongoDB，存储以下数据：

#### 游戏数据

```json
{
  "gameId": "xxx",
  "userAnswerEncrypted": "xxx",
  "agentAnswerEncrypted": "xxx",
  "rounds": [
    {
      "question": "是否属于计算机",
      "answer": "是",
      "notes": "可能是软件"
    }
  ],
  "status": "playing"
}
```

------

#### 用户记录

- 历史游戏
- 推理笔记
- 常用策略

------

## 技术选型（重构结论）

### 后端（核心推荐）

- FastAPI（主服务）
- LangChain（Python版）
- DeepSeek API（LLM能力）

原因：

- Python 在 Agent 生态更成熟
- LangChain Python 支持更完整
- 更适合复杂推理与多轮控制

------

### 前端

- Vue 3 + Vite
- Pinia（状态管理）
- 移动端 H5（优先）

------

### 数据库

- MongoDB（文档型数据更适合对话与回合记录）

------

### 部署

- 初期：本地运行
- 后期：Docker + Docker Compose

------

## 系统调用关系

```text
[ H5前端 ]
     ↓
[ FastAPI ]
     ↓
[ Agent控制层（LangChain） ]
     ↓
[ DeepSeek模型 ]

同时：
FastAPI ↔ MongoDB
FastAPI ↔ 加密模块
用户 ↔ 小助手（独立调用）
```

------

## MVP（最小可行版本）

优先实现：

- 用户 vs Agent 猜词
- 基础加密 / 解密
- 简单回合制问答
- 基础上下文记录
- 小助手（简单问答版）

------

## 后续扩展方向

### 功能扩展

- 多人对战（WebSocket）
- 语音输入（Web Speech API / App）
- 智能提示优化（策略级提示）
- 排行榜与成就系统

------

### 技术演进

- Agent 多工具调用（Tool Calling）
- 引入向量数据库（增强记忆）
- Prompt工程优化（核心提升点）

------

## 项目实现建议

优先路径：

```text
第一步：FastAPI + DeepSeek（无LangChain）
第二步：补充游戏规则（最核心）
第三步：接入MongoDB
第四步：引入LangChain优化Agent
第五步：增加小助手能力
```

------

## 总结

该项目的本质并不在于技术栈本身，而在于：

- 游戏规则是否合理
- Agent 是否“像人一样推理”
- 小助手是否“强但不过界”

通过将 Agent、加密机制与用户辅助工具解耦，系统既保证了公平性，又增强了可玩性与学习价值

建议优先完成最小闭环，再逐步增强 Agent 能力与交互体验，从而演进为一个真正具有策略深度的智能游戏系统

## draw.io 泳道图（XML）

```xml
<mxfile host="app.diagrams.net">
  <diagram name="Swimlane-GuessWordAgent">
    <mxGraphModel dx="1600" dy="900" grid="1" gridSize="10">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- 泳道：用户 -->
        <mxCell id="lane_user" value="用户" style="swimlane;horizontal=0;startSize=30;fillColor=#f8cecc;" vertex="1" parent="1">
          <mxGeometry x="0" y="0" width="300" height="900" as="geometry"/>
        </mxCell>

        <!-- 泳道：小助手 -->
        <mxCell id="lane_helper" value="小助手（用户侧）" style="swimlane;horizontal=0;startSize=30;fillColor=#d5e8d4;" vertex="1" parent="1">
          <mxGeometry x="300" y="0" width="300" height="900" as="geometry"/>
        </mxCell>

        <!-- 泳道：Agent -->
        <mxCell id="lane_agent" value="Agent（游戏控制）" style="swimlane;horizontal=0;startSize=30;fillColor=#dae8fc;" vertex="1" parent="1">
          <mxGeometry x="600" y="0" width="350" height="900" as="geometry"/>
        </mxCell>

        <!-- 泳道：系统 -->
        <mxCell id="lane_system" value="加密模块 + 数据库" style="swimlane;horizontal=0;startSize=30;fillColor=#fff2cc;" vertex="1" parent="1">
          <mxGeometry x="950" y="0" width="350" height="900" as="geometry"/>
        </mxCell>

        <!-- 开始 -->
        <mxCell id="start" value="开始游戏\n输入答案 + 密钥" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="lane_user">
          <mxGeometry x="50" y="60" width="200" height="70" as="geometry"/>
        </mxCell>

        <!-- 加密 -->
        <mxCell id="encrypt" value="答案加密" style="rounded=1;" vertex="1" parent="lane_system">
          <mxGeometry x="80" y="60" width="200" height="70" as="geometry"/>
        </mxCell>

        <!-- Agent初始化 -->
        <mxCell id="init" value="初始化游戏\n(生成Agent答案+上下文)" style="rounded=1;" vertex="1" parent="lane_agent">
          <mxGeometry x="80" y="160" width="220" height="80" as="geometry"/>
        </mxCell>

        <!-- 用户提问 -->
        <mxCell id="ask" value="提问(是/否)" style="rounded=1;" vertex="1" parent="lane_user">
          <mxGeometry x="50" y="220" width="200" height="60" as="geometry"/>
        </mxCell>

        <!-- 小助手咨询 -->
        <mxCell id="helper_use" value="查询提示/知识" style="rounded=1;" vertex="1" parent="lane_helper">
          <mxGeometry x="50" y="320" width="200" height="70" as="geometry"/>
        </mxCell>

        <!-- Agent处理 -->
        <mxCell id="process" value="解析问题\nLLM推理\n生成回答" style="rounded=1;" vertex="1" parent="lane_agent">
          <mxGeometry x="80" y="260" width="220" height="90" as="geometry"/>
        </mxCell>

        <!-- 返回回答 -->
        <mxCell id="answer" value="返回 是/否" style="rounded=1;" vertex="1" parent="lane_user">
          <mxGeometry x="50" y="420" width="200" height="60" as="geometry"/>
        </mxCell>

        <!-- 记录 -->
        <mxCell id="log" value="记录轮次/上下文" style="rounded=1;" vertex="1" parent="lane_system">
          <mxGeometry x="80" y="260" width="220" height="70" as="geometry"/>
        </mxCell>

        <!-- 猜测 -->
        <mxCell id="guess" value="猜测答案" style="rounded=1;" vertex="1" parent="lane_user">
          <mxGeometry x="50" y="520" width="200" height="60" as="geometry"/>
        </mxCell>

        <!-- 校验 -->
        <mxCell id="verify" value="校验答案(密文比对)" style="rounded=1;" vertex="1" parent="lane_system">
          <mxGeometry x="80" y="520" width="220" height="70" as="geometry"/>
        </mxCell>

        <!-- 游戏结束 -->
        <mxCell id="end" value="游戏结束\n输入密钥解密" style="rounded=1;" vertex="1" parent="lane_user">
          <mxGeometry x="50" y="640" width="200" height="70" as="geometry"/>
        </mxCell>

        <!-- 解密 -->
        <mxCell id="decrypt" value="解密答案" style="rounded=1;" vertex="1" parent="lane_system">
          <mxGeometry x="80" y="640" width="220" height="70" as="geometry"/>
        </mxCell>

        <!-- 连线 -->
        <mxCell id="e1" edge="1" parent="1" source="start" target="encrypt"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e2" edge="1" parent="1" source="encrypt" target="init"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e3" edge="1" parent="1" source="init" target="ask"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e4" edge="1" parent="1" source="ask" target="process"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e5" edge="1" parent="1" source="process" target="answer"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e6" edge="1" parent="1" source="process" target="log"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e7" edge="1" parent="1" source="answer" target="guess"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e8" edge="1" parent="1" source="guess" target="verify"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e9" edge="1" parent="1" source="verify" target="end"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e10" edge="1" parent="1" source="end" target="decrypt"><mxGeometry relative="1" as="geometry"/></mxCell>

        <!-- 小助手独立链路 -->
        <mxCell id="e11" edge="1" parent="1" source="ask" target="helper_use"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e12" edge="1" parent="1" source="helper_use" target="ask"><mxGeometry relative="1" as="geometry"/></mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```