from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入路由
from .api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("🚀 Starting whale-land-VLM backend server...")
    yield
    # 关闭时执行
    print("👋 Shutting down whale-land-VLM backend server...")

app = FastAPI(
    title="Whale Land VLM API",
    description="鲸娱秘境 - VLLM结合线下密室的人工智能创新应用 API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Whale Land VLM API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
