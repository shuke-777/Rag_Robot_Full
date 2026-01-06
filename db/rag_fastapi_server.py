"""
FastAPI 服务版本的 RAG 系统
基于 rag_with_async_table.py，不改动原有代码，只是添加 API 接口
"""
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional
import json

# 导入原有的数据库操作函数和配置
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from contextlib import asynccontextmanager
from Sql_base import MessagesTableNew, SessionTable, base
from langchain_core.chat_history import AIMessage, HumanMessage, BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from v2_rag_with_stream_async import (
    llm,
    load_vector_store,
    create_history_aware_retriever_chain,
    create_qa_chain,
    RunnableWithMessageHistory
)

# ==================== 数据库配置 ====================
db_url = 'mysql+aiomysql://shuke:123456@localhost/sk_db?charset=utf8mb4'
engine = create_async_engine(url=db_url)
async_session = async_sessionmaker(bind=engine)

@asynccontextmanager
async def get_async_db():
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()

# ==================== 数据库操作函数（复用原有逻辑）====================
async def save_history_db(session_id: str, content: str, role: str):
    """保存消息到数据库"""
    async with get_async_db() as db:
        try:
            query_content = select(SessionTable).where(SessionTable.session_id == session_id)
            session_result = await db.execute(query_content)
            session_result = session_result.scalar_one_or_none()
            if not session_result:
                session1 = SessionTable(session_id=session_id)
                db.add(session1)
                await db.commit()
                await db.refresh(session1)
                session_result = session1
            message_add_content = MessagesTableNew(
                content=content,
                role=role,
                session_id=session_result.id
            )
            db.add(message_add_content)
            await db.commit()
            print(f'[数据库] 消息保存成功 - session_id: {session_id}, role: {role}')
        except Exception as e:
            await db.rollback()
            print(f'[数据库] 保存失败: {e}')
            raise

async def load_db_history(session_id: str):
    """从数据库加载历史消息"""
    async with get_async_db() as db:
        load_history = ChatMessageHistory()
        query_content = select(SessionTable).where(SessionTable.session_id == session_id)
        result = await db.execute(query_content)
        result = result.scalar_one_or_none()
        if result:
            query1 = select(MessagesTableNew).where(MessagesTableNew.session_id == result.id)
            result2 = await (db.execute(query1))
            result2 = result2.scalars().all()
            for result_i in result2:
                if result_i.role == 'ai':
                    load_history.add_ai_message(AIMessage(content=result_i.content))
                else:
                    load_history.add_user_message(HumanMessage(content=result_i.content))
        print(f'[数据库] 历史加载完成 - session_id: {session_id}, 消息数: {len(load_history.messages)}')
        return load_history

# ==================== 内存存储（复用原有逻辑）====================
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """从内存获取会话历史"""
    if session_id not in store:
        print(f'[内存] session {session_id} 未在缓存中，返回空历史')
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# ==================== RAG 链初始化 ====================
from config.path_config import VECTOR_STORE_DIR
print('[初始化] 正在加载向量库...')
local_store = str(VECTOR_STORE_DIR / '1201Faiss.faiss')
embed = load_vector_store(local_store)
retriever = embed.as_retriever(search_kwargs={'k': 3})
retriever_chain = create_history_aware_retriever_chain(llm=llm, retriever=retriever)
qa_chain = create_qa_chain(llm=llm, history_aware_retriever=retriever_chain)

def get_rag_chain_session(rag_chain, get_session):
    """创建带历史管理的RAG链"""
    rag_chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session,
        input_messages_key='input',
        history_messages_key='chat_history',
    )
    return rag_chain_with_history

rag_chain = get_rag_chain_session(qa_chain, get_session=get_session_history)
print('[初始化] RAG 链创建完成！')

# ==================== FastAPI 应用 ====================
app = FastAPI(
    title="RAG 问答系统 API",
    description="基于 LangChain 的 RAG 流式问答系统",
    version="1.0.0"
)

# 配置 CORS（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请改为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 请求/响应模型 ====================
class ChatRequest(BaseModel):
    """问答请求"""
    query: str
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "什么是工具函数？",
                "session_id": "test_session_001"
            }
        }

class ChatResponse(BaseModel):
    """问答响应（非流式）"""
    response: str
    session_id: str

class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    message_count: int

# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RAG 问答系统 API",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "session_info": "/api/session/{session_id}"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    普通问答接口（非流式）

    - **query**: 用户问题
    - **session_id**: 会话ID，用于管理对话历史
    """
    try:
        # 1. 预加载历史（如果内存中没有，则从数据库加载）
        if request.session_id not in store:
            print(f'[预加载] 从数据库加载 session: {request.session_id}')
            store[request.session_id] = await load_db_history(request.session_id)

        # 2. 调用 RAG 链（非流式）
        print(f'[问答] 收到问题: {request.query}')
        result = await rag_chain.ainvoke(
            {'input': request.query},
            config={'configurable': {'session_id': request.session_id}}
        )

        response = result
        print(f'[问答] 回答生成完成')

        # 3. 保存到数据库
        messages = store[request.session_id].messages[-2:]
        for msg in messages:
            role = 'ai' if isinstance(msg, AIMessage) else 'human'
            await save_history_db(request.session_id, msg.content, role)

        return ChatResponse(
            response=response,
            session_id=request.session_id
        )

    except Exception as e:
        print(f'[错误] {e}')
        raise

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式问答接口（Server-Sent Events）

    - **query**: 用户问题
    - **session_id**: 会话ID，用于管理对话历史

    返回格式：SSE (text/event-stream)
    每个数据块格式：data: {chunk}\n\n
    """
    async def generate():
        try:
            # 1. 预加载历史（如果内存中没有，则从数据库加载）
            if request.session_id not in store:
                print(f'[预加载] 从数据库加载 session: {request.session_id}')
                store[request.session_id] = await load_db_history(request.session_id)
                print(f'[预加载] 已加载 {len(store[request.session_id].messages)} 条历史消息')

            # 2. 流式调用 RAG 链
            print(f'[流式问答] 收到问题: {request.query}')
            full_response = ""

            result = rag_chain.astream(
                {'input': request.query},
                config={'configurable': {'session_id': request.session_id}}
            )

            async for chunk in result:
                full_response += chunk
                # SSE 格式：data: {content}\n\n
                yield f"data: {chunk}\n\n"

            print(f'[流式问答] 回答生成完成，长度: {len(full_response)}')

            # 3. 保存到数据库（最后两条消息：用户问题 + AI回答）
            messages = store[request.session_id].messages[-2:]
            for msg in messages:
                role = 'ai' if isinstance(msg, AIMessage) else 'human'
                await save_history_db(request.session_id, msg.content, role)

            # 4. 发送完成信号
            yield f"data: [DONE]\n\n"

        except Exception as e:
            print(f'[错误] 流式问答失败: {e}')
            error_msg = json.dumps({"error": str(e)})
            yield f"data: {error_msg}\n\n"

    return EventSourceResponse(generate())

@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """
    获取会话信息

    - **session_id**: 会话ID

    返回该会话的消息数量
    """
    try:
        # 如果内存中有，直接返回
        if session_id in store:
            message_count = len(store[session_id].messages)
        else:
            # 从数据库加载
            history = await load_db_history(session_id)
            message_count = len(history.messages)

        return SessionInfo(
            session_id=session_id,
            message_count=message_count
        )

    except Exception as e:
        print(f'[错误] 获取会话信息失败: {e}')
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    print('[关闭] 正在清理资源...')
    await engine.dispose()
    print('[关闭] 资源清理完成')

# ==================== 启动服务 ====================
if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*50)
    print("🚀 RAG 问答系统 API 服务启动")
    print("="*50)
    print(f"📖 API 文档: http://localhost:8000/docs")
    print(f"📖 交互式文档: http://localhost:8000/redoc")
    print(f"💬 问答接口: POST http://localhost:8000/api/chat")
    print(f"🌊 流式接口: POST http://localhost:8000/api/chat/stream")
    print("="*50 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",  # 允许外部访问
        port=8000,
        log_level="info"
    )
