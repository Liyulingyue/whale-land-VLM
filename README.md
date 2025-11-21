# 🐋 鲸娱秘境 Whale Land VLM

MLLM结合线下密室的人工智能创新应用

## 📁 项目结构

```
whale-land-VLM/
├── backend/              # FastAPI 后端服务
│   ├── app.py           # 主应用入口
│   ├── requirements.txt # Python 依赖
│   ├── .env.example     # 环境变量模板
│   ├── api/             # API 路由
│   ├── src/             # 核心业务逻辑
│   └── config/          # 游戏配置文件
│
├── frontend/            # React + TypeScript 前端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
└── gradio_demo/         # Gradio 原型演示
    ├── gradio_with_state.py
    ├── src/             # 共享的核心逻辑
    └── config/          # 游戏配置
```

## 🚀 快速开始

### 后端 Backend

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 API keys

# 启动服务器
python app.py
```

后端将在 http://localhost:8000 启动

API 文档：http://localhost:8000/docs

### 前端 Frontend

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动（或其他可用端口）

**访问应用：** 打开浏览器访问前端地址，即可开始游戏！

### Gradio 演示 (可选)

```bash
# 进入 gradio_demo 目录
cd gradio_demo

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env

# 启动 Gradio 界面
python gradio_with_state.py
```

## 🏗️ 架构说明

### Backend (FastAPI)

完全重构的后端服务，基于 gradio_demo 的核心逻辑：

- ✅ RESTful API 设计
- ✅ 会话管理
- ✅ 多模态输入支持（文本、图片）
- ✅ 支持多种 LLM 后端（OpenAI、智谱、SiliconFlow、OpenVINO）
- ✅ CORS 配置用于前后端分离
- ✅ 完整的 API 文档（Swagger UI）

**核心 API 端点：**
- `POST /api/session/create` - 创建游戏会话
- `POST /api/chat` - 文本对话
- `POST /api/item/submit` - 提交物品
- `POST /api/image/upload` - 上传图片识别

### Frontend (React + TypeScript)

现代化的 Web 前端界面：

- **主页** (`/`) - 精美的游戏介绍页面
  - 渐变背景设计
  - 特性展示（智能对话、图像识别、角色扮演）
  - 开始游戏按钮
  
- **聊天界面** (`/chat`) - 类似微信的对话体验
  - 💬 实时文本对话
  - 📷 相机拍照上传
  - 🖼️ 图片选择上传
  - 🎮 游戏状态显示
  - 🔄 重置游戏功能
  
**技术栈：**
- React 19 + TypeScript
- React Router - 路由管理
- Axios - HTTP 客户端
- Vite - 快速构建
- Lucide React - 图标库

**响应式设计：** 完美适配桌面端和移动端

### Gradio Demo

原型演示系统，保留用于快速测试：

- 集成 Gradio UI
- 包含完整的游戏逻辑
- 适合快速原型验证

## 🔧 环境变量配置

在 `backend/.env` 文件中配置：

```env
# LLM 后端选择
LLM_BACKEND=openai  # openai, zhipu, siliconflow, openvino

# API Keys
OPENAI_API_KEY=sk-xxx
ZHIPU_API_KEY=xxx

# 模型配置
MODEL_NAME=gpt-4o-mini

# 服务器端口
PORT=8000
```

## 📝 游戏配置

游戏剧情在 `backend/config/*.yaml` 中定义：

```yaml
prompt_steps:
  - welcome_info: "欢迎来到游戏..."
    prompt: "你是一个..."
    conds: [["物品1", "物品2"]]

items:
  - name: "物品名称"
    text: "NPC回复文本"
    img_path: "图片路径"
```

## 🔄 从 Gradio Demo 迁移

backend 重构保留了 gradio_demo 的所有核心功能：

| gradio_demo | backend 对应 |
|------------|-------------|
| `src/GameMaster.py` | `backend/src/GameMaster.py` |
| `src/llm_response.py` | `backend/src/llm_response.py` |
| `config/*.yaml` | `backend/config/*.yaml` |
| Gradio UI | FastAPI REST API |

## 🛠️ 开发指南

### 添加新主题

1. 在 `backend/config/` 创建新的 YAML 文件
2. 定义 `prompt_steps` 和 `items`
3. 创建会话时指定配置文件路径

### 扩展 API

1. 在 `backend/api/routes.py` 添加新路由
2. 遵循现有的模式和错误处理
3. 更新 API 文档

## 📦 依赖说明

### Backend
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `openai` / `zhipuai` - LLM 客户端
- `pillow` - 图像处理
- `pyyaml` - 配置解析

### Frontend
- `react` - UI 框架
- `vite` - 构建工具
- `typescript` - 类型系统

## 📄 License

参见项目 LICENSE 文件

## 🙏 致谢

基于 gradio_demo 重构，保留了原有的游戏逻辑和 AI 集成。
