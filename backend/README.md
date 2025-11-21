# Whale Land VLM Backend

鲸娱秘境后端服务 - 基于 FastAPI 的 MLLM 密室逃脱游戏 API

## 项目结构

```
backend/
├── app.py                 # FastAPI 应用主入口
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量示例
├── api/                  # API 路由
│   ├── __init__.py
│   └── routes.py         # 所有 API 端点定义
├── src/                  # 核心业务逻辑
│   ├── __init__.py
│   ├── GameMaster.py     # 游戏主控制器
│   ├── llm_response.py   # LLM 响应处理
│   ├── parse_json.py     # JSON 解析工具
│   ├── recognize_from_image_glm.py  # 图像识别
│   └── resize_img.py     # 图片处理工具
├── config/               # 游戏配置文件
│   ├── police.yaml       # 警察主题配置
│   └── ...               # 其他主题配置
└── models/               # 模型文件（如需要）
```

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境（如果有）
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
copy .env.example .env

# 编辑 .env 文件，填入你的 API keys
```

### 3. 运行服务器

```bash
# 开发模式（带热重载）
python app.py

# 或使用 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

服务器将在 http://localhost:8000 启动

## API 文档

启动服务器后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要 API 端点

### 会话管理
- `POST /api/session/create` - 创建新游戏会话
- `GET /api/session/{session_id}/status` - 获取会话状态
- `POST /api/session/{session_id}/reset` - 重置会话
- `DELETE /api/session/{session_id}` - 删除会话

### 游戏交互
- `POST /api/chat` - 发送聊天消息
- `POST /api/item/submit` - 提交物品
- `POST /api/image/submit` - 提交图片（base64）
- `POST /api/image/upload` - 上传图片文件
- `GET /api/items/{session_id}` - 获取可用物品列表

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_BACKEND` | LLM 后端类型 | `openai` |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `ZHIPU_API_KEY` | 智谱 AI API Key | - |
| `MODEL_NAME` | 使用的模型名称 | `gpt-4o-mini` |
| `PORT` | 服务器端口 | `8000` |

## 支持的 LLM 后端

- **OpenAI** - GPT-4, GPT-3.5 等
- **SiliconFlow** - 国内 AI 服务
- **Zhipu AI** - 智谱 GLM 系列
- **OpenVINO** - 本地推理

## 开发说明

### 添加新的游戏主题

1. 在 `config/` 目录下创建新的 YAML 配置文件
2. 参考 `police.yaml` 的格式定义游戏流程
3. 创建会话时指定配置文件路径

### 会话状态管理

当前使用内存存储会话状态。生产环境建议：
- 使用 Redis 存储会话
- 实现会话过期机制
- 添加用户认证

## 与 gradio_demo 的关系

本项目基于 `gradio_demo` 重构：
- 复用核心游戏逻辑（GameMaster 等）
- 将 Gradio UI 替换为 RESTful API
- 支持前后端分离架构
- 便于集成到 React/Vue 等现代前端框架

## License

参考主项目 LICENSE
