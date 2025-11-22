#!/usr/bin/env python3
"""
启动脚本 - 用于启动 whale-land-VLM 后端服务器
"""

import os
import sys
from pathlib import Path
import uvicorn

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting whale-land-VLM backend server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)