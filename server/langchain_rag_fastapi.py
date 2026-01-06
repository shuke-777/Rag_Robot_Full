from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,FileResponse
from fastapi.staticfiles import StaticFiles
import sys
from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
sys.path.append(str(DB_DIR))
from rag_with_async_table import main,invoke_save,single_question,rag_chain
import uvicorn
import os
import json
from sse_starlette.sse import EventSourceResponse

app = FastAPI(
    title='RAG问答系统API',
    description='基于RAG问答系统的API接口',
    version='0.1.0'
)

#这样谁都可以访问我的后端
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径返回前端页面
@app.get('/')
async def read_index():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "欢迎使用 RAG 问答系统 API，请访问 /docs 查看接口文档"}

@app.get('/chat_stream/{question}')
async def chat_stream(question:str,session_id:str):
    async def generate():
        async for chunk in single_question(
            session_id=session_id,
            query=question,
            rag = rag_chain
        ):
            # 将chunk包装成JSON格式，符合前端期待
            data = {"data": chunk}
            json_str = json.dumps(data, ensure_ascii=False)
            print(f"[DEBUG] 发送数据: {json_str}")  # 调试输出
            yield json_str
    return EventSourceResponse(generate())

# 挂载静态文件目录（放在最后）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

