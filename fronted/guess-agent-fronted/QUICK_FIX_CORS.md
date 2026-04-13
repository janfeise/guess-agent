# 🔧 CORS 问题快速修复指南

## 问题

前端看到浏览器控制台错误：

```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/health' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ 已完成的修复

### 前端修改（已完成）

1. **Vite 代理配置** (`vite.config.ts`)
   - ✅ 添加 `/api` 代理到 `http://localhost:8000`
   - 效果：开发时自动转发 API 请求，绕过 CORS

2. **API 客户端更新** (`src/services/gameApiClient.ts`)
   - ✅ 支持相对路径 `/api/v1`
   - ✅ 自适应环境配置
   - 效果：自动使用代理或完整 URL

3. **文档** (`CORS_CONFIGURATION.md`)
   - ✅ 完整的 CORS 配置指南
   - ✅ 后端配置示例（FastAPI）

---

## 🚀 立即修复（3 步）

### 步骤 1：重启开发服务器

```bash
# 停止现有服务器（Ctrl+C）

# 重新启动
npm run dev
```

**结果**：Vite 代理会自动应用

### 步骤 2：清除浏览器缓存

在浏览器按 `F12` 打开开发者工具：

- 右键点击刷新按钮 → "清空缓存并硬性重新加载"
- 或按 `Ctrl+Shift+Delete`

### 步骤 3：访问前端

打开 http://localhost:3000

**预期结果**：

- ✅ 不再看到 CORS 错误
- ✅ API 状态应显示"在线"（绿色）
- ✅ 可以正常使用游戏功能

---

## 📝 工作原理

### 之前（❌ 有 CORS 错误）

```
浏览器 (localhost:3000)
  ↓ 直接请求
后端 (localhost:8000)
  ↗ 未授权 + CORS 错误
```

### 之后（✅ 正常工作）

```
浏览器 (localhost:3000)
  ↓ 请求 /api/v1/health
Vite 代理 (localhost:5173)
  ↓ 转发请求
后端 (localhost:8000)
  ↓ 返回响应
Vite 代理
  ↓ 返回给浏览器
浏览器 ✅ 成功
```

---

## ⚙️ 验证配置

### 检查点 1：Vite 配置

打开 `vite.config.ts`，应该看到：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

✅ 状态：已配置

### 检查点 2：API 客户端

打开 `src/services/gameApiClient.ts`，应该支持：

- 相对 URL：`/api/v1` ← 使用代理
- 完整 URL：`http://localhost:8000/api/v1` ← 生产环境

✅ 状态：已更新

### 检查点 3：环境配置

查看 `.env.local`：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

💡 说明：此配置仅在 Vite 代理不可用时使用

✅ 状态：已有备选配置

---

## 🧪 测试 API 连接

### 方法 1：浏览器控制台

打开浏览器开发者工具（F12）→ 控制台：

```javascript
// 测试 API 连接
fetch("/api/v1/health")
  .then((r) => {
    console.log("✅ API 连接成功");
    console.log("状态码:", r.status);
    console.log("响应头:", r.headers);
    return r.json();
  })
  .then((data) => console.log("响应数据:", data))
  .catch((err) => console.error("❌ 错误:", err));
```

### 方法 2：Network 标签

1. 打开开发者工具 → Network 标签
2. 访问应用首页
3. 查找 `/api/v1/health` 请求
4. 检查：
   - ✅ 状态码应为 `200`
   - ✅ Response 头应包含"Access-Control-Allow-Origin"（如果启用了后端 CORS）
   - ✅ Response body 应为健康检查数据

### 方法 3：直接访问

在新标签页访问：

```
http://localhost:3000/api/v1/health
```

应该看到 JSON 响应（如果配置正确）

---

## ⚠️ 常见问题

### Q1：修改后仍然看到 CORS 错误

**解决步骤**：

1. 检查服务器是否真的重启了
2. 清除浏览器缓存（Ctrl+Shift+Delete）
3. 检查控制台输出是否显示代理已激活
4. 确认后端确实运行在 `http://localhost:8000`

### Q2：看到 "Cannot GET /api/v1/health"

**原因**：Vite 代理可能不工作，请求到达了 frontend 而非后端
**解决**：

1. 检查后端是否运行
2. 重启 dev 服务器（npm run dev）
3. 查看 terminal 输出中的代理日志

### Q3：错误 "ERR_CONNECTION_REFUSED"

**原因**：后端未运行或地址不对
**解决**：

1. 启动后端服务
2. 验证后端运行在 `http://localhost:8000`
3. 在浏览器中直接访问测试：`curl http://localhost:8000/api/v1/health`

---

## 🔄 完整流程

```
1. 启动前端
   npm run dev
   ↓
2. Vite 代理激活
   监听 /api/* 请求
   ↓
3. 启动后端
   python -m backend.main
   ↓
4. 访问 http://localhost:3000
   ↓
5. 前端请求 /api/v1/health
   ↓
6. Vite 代理转发到 http://localhost:8000/api/v1/health
   ↓
7. 后端返回响应
   ↓
8. 浏览器收到（无 CORS 错误）✅
```

---

## 📦 生产环境注意

此代理配置 **仅用于开发环境**。

生产环境需要后端配置 CORS：

```python
# 后端需要配置
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

详见：[CORS_CONFIGURATION.md](./CORS_CONFIGURATION.md)

---

## ✨ 总结

| 项目       | 状态        | 效果               |
| ---------- | ----------- | ------------------ |
| Vite 代理  | ✅ 配置完成 | 绕过 CORS 限制     |
| API 客户端 | ✅ 已更新   | 支持代理和完整 URL |
| 文档       | ✅ 已编写   | 完整配置指南       |

**下一步**：重启服务器并刷新浏览器！

---

**最后修复时间**：2026-04-13  
**修复人员**：GitHub Copilot
