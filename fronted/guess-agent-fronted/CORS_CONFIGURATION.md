# CORS 配置指南

## 问题描述

前端（http://localhost:3000）和后端（http://localhost:8000）在不同的域/端口上运行，导致 CORS（跨域资源共享）问题。

浏览器控制台错误：

```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/health' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

---

## 解决方案

### 1. 开发环境（推荐）

#### 前端 Vite 代理方案 ✅ **已配置**

前端项目已配置 Vite 代理，开发时自动转发 `/api/*` 请求到后端：

**vite.config.ts**

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

**优点**：

- 无需修改后端代码
- 完全绕过 CORS 限制
- 开发体验更好

**使用方法**：

```bash
npm run dev
```

---

### 2. 后端 CORS 配置（生产环境必需）

#### Python FastAPI 后端

在后端 `main.py` 或主应用文件中添加 CORS 中间件：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # 本地开发前端
        "http://localhost:5173",      # Vite 默认端口
        "https://example.com",        # 生产前端域名（按需添加）
    ],
    allow_credentials=True,
    allow_methods=["*"],              # 允许所有 HTTP 方法
    allow_headers=["*"],              # 允许所有请求头
)

# ... 其他配置
```

#### 环境变量配置（推荐）

创建 `.env` 文件：

```env
# 后端 CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://example.com
```

在代码中使用：

```python
import os
from fastapi.middleware.cors import CORSMiddleware

cors_origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 3. 不同部署场景

#### 本地开发

✅ **前端**：使用 Vite 代理（已配置）

```bash
npm run dev  # 自动代理到 http://localhost:8000
```

⚠️ **后端**：如果后端也在本地开发，无需配置 CORS（代理已处理）

#### Docker/容器开发

如果使用 Docker Compose，确保后端配置 CORS：

```yaml
version: "3.8"
services:
  frontend:
    image: node:19
    ports:
      - "3000:5173"
    environment:
      - VITE_API_BASE_URL=http://backend:8000/api/v1

  backend:
    image: python:3.11
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

#### 生产环境

**方式1：后端配置 CORS（推荐）**

```python
CORS_ORIGINS=https://example.com,https://www.example.com
```

**方式2：Nginx 反向代理**

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

location / {
    proxy_pass http://frontend:3000;
}
```

---

## 前端配置详解

### 环境变量

**`.env.local`（开发环境）**

```env
VITE_API_BASE_URL=/api/v1
```

**`.env.production`（生产环境）**

```env
VITE_API_BASE_URL=https://api.example.com/api/v1
```

### API 客户端自适应

API 客户端会根据环境自动选择 URL：

```typescript
// 开发环境：使用相对路径 /api/v1（Vite 代理处理）
// 生产环境：使用完整 URL（如 https://api.example.com/api/v1）
```

---

## 故障排查

### 症状 1：仍然看到 CORS 错误

**检查清单**：

1. ✅ 后端 CORS 中间件是否已配置？
2. ✅ 允许的源 URL 是否正确（包括协议和端口）？
3. ✅ `Allow-Control-Allow-Origin` 响应头是否存在？

**验证响应头**：

```bash
curl -I http://localhost:8000/api/v1/health
# 应该看到：
# Access-Control-Allow-Origin: http://localhost:3000
```

### 症状 2：预检请求失败（OPTIONS）

**问题**：CORS 预检请求被拒绝
**解决**：确保 `allow_methods=["*"]` 包含 OPTIONS

```python
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 包含 OPTIONS
    # ...
)
```

### 症状 3：凭证（Cookies）无法发送

**解决**：启用凭证支持

```python
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # 必需
    # ...
)
```

前端需要明确指定发送凭证：

```typescript
axios.create({
  withCredentials: true, // 发送 cookies
});
```

---

## 安全建议

### 生产环境

⚠️ **不要使用**：

```python
allow_origins=["*"]  # 风险：允许所有来源
```

✅ **推荐**：

```python
# 只允许特定域名
allow_origins=[
    "https://example.com",
    "https://www.example.com",
]
```

### 请求头限制

根据需求限制允许的请求头：

```python
allow_headers=[
    "Content-Type",
    "Authorization",
    # 按需添加
]
```

---

## 测试 CORS

### 使用 curl 测试

```bash
# 简单请求
curl http://localhost:8000/api/v1/health

# 检查 CORS 响应头
curl -I http://localhost:8000/api/v1/health

# 预检请求
curl -X OPTIONS http://localhost:8000/api/v1/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"
```

### 浏览器控制台测试

```javascript
fetch("http://localhost:8000/api/v1/health", {
  method: "GET",
  credentials: "include",
})
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);
```

---

## 总结

| 环境         | 前端配置     | 后端配置       | 状态   |
| ------------ | ------------ | -------------- | ------ |
| **本地开发** | ✅ Vite 代理 | ⚠️ 可选        | 工作中 |
| **Docker**   | ✅ 相对 URL  | ✅ CORS 中间件 | 需要   |
| **生产**     | ✅ 完整 URL  | ✅ CORS 中间件 | 需要   |

---

## 参考链接

- [FastAPI CORS 文档](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS 指南](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Vite 代理配置](https://vitejs.dev/config/server-options.html#server-proxy)

---

**更新日期**：2026-04-13  
**适用版本**：前端 v1.0+
