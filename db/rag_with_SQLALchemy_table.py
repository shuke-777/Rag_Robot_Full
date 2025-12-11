import asyncio
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base,Mapped,MappedColumn,relationship
from typing import List
from sqlalchemy import ForeignKey,Text,String,select
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from v2_rag_with_stream_async import *
from Sql_base import base as Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
load_dotenv()
class Session (Base):
    __tablename__ = 'session_table'
    id : Mapped[int] = MappedColumn(primary_key=True)
    sessions_id :Mapped[str] = MappedColumn(String(10))
    messages :Mapped[List['Messages']] = relationship(
        'Messages',
        back_populates= 'sessions',
        cascade="all, delete-orphan",
    )
class Messages(Base):
    __tablename__ = 'messages_table'
    id : Mapped[int] = MappedColumn(primary_key=True)
    session_id :Mapped[int] = MappedColumn(ForeignKey('session_table.id'))
    content : Mapped[str] = MappedColumn(Text)
    role : Mapped[str] = MappedColumn(String(10))
    #这里不用做List了，因为这里不用做一对多的，直接就是对应一个就行了
    sessions : Mapped['Session'] = relationship(
        'Session',
        back_populates='messages',

    )
url = 'mysql+aiomysql://shuke:123456@localhost/sk_db?charset=utf8mb4'
engine = create_async_engine(
    url=url
)
AsyncSessionLocal = async_sessionmaker(bind = engine, expire_on_commit=False)
##asyncsql操作
@asynccontextmanager
async def get_async_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
#async save_message
async def db_save_message(session_id:str,role:str,content:str):
    async with get_async_db() as db:
        try:
            query_content = select(Session).where(Session.sessions_id == session_id)
            session_result = (await db.execute(query_content)).scalar_one_or_none()

            if not session_result:
                session1 = Session(sessions_id = session_id)
                db.add(session1)
                await db.commit()
                await db.refresh(session1)
                session_result = session1
            #添加消息
            #这里就直接通过session_id来添加了，不用再做relationship了
            message = Messages(content = content,role = role,session_id = session_result.id)
            db.add(message)
            await db.commit()
            print('数据添加成功')
        except Exception as e:
            await db.rollback()
            print(f'数据库添加失败{e}')

#async load_history
async def db_load_history(session_id:str):
    load_history = ChatMessageHistory()
    async with get_async_db() as db:
        try:
            query_1 = select(Session).where(Session.sessions_id == session_id)
            session_result = (await db.execute(query_1)).scalar_one_or_none()
            if session_result:
                #query_2 = select(Messages).where(Messages.session_id == session_result.id)
                query_2 = select(Messages).where(Messages.session_id ==
                                                 session_result.id).order_by(Messages.id)
                message_result = (await db.execute(query_2)).scalars().all()
                for message_i in message_result:
                    if message_i.role == 'ai':
                        load_history.add_ai_message(AIMessage(content=message_i.content))
                    elif message_i.role == 'human':
                        load_history.add_user_message(HumanMessage(content=message_i.content))
        except Exception as e:
            await db.rollback()
            print(f'数据库加载history失败{e}')
    return load_history
store = {}
async def get_session_history(session_id:str):
   if session_id not in store:
       print(f'[缓存未命中]从数据库加载session:{session_id}')
       store [session_id] = await db_load_history(session_id)
   else:
       print(f'[缓存命中]session:{session_id}')
   return store[session_id]

async def invoke_save(rag,session_id:str,role:str,input_text:str):
    result = await rag.ainvoke({'input':input_text},
                               config = {'configurable':{'session_id':session_id}})
    print(result)
    print(type(result))
    answer = result
    print(f'[AI回复]:{answer}')

    #save_db
    await db_save_message(session_id,'human',input_text)
    await db_save_message(session_id,'ai',answer)
    return answer

def get_rag_chain_session(rag_chain,get_session):
    """创建带历史管理的RAG链"""
    rag_chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session,
        input_messages_key='input',
        history_messages_key='chat_history',
    )
    return rag_chain_with_history

if __name__ == '__main__':
    async def main():
        local_store = '/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/vector_store/1201Faiss.faiss'
        embed = load_vector_store(local_store)
        retriever = embed.as_retriever(search_kwargs={'k': 3})
        retriever_chain = create_history_aware_retriever_chain(llm = llm,retriever = retriever)
        qa_chain = create_qa_chain(llm = llm,history_aware_retriever=retriever_chain)
        rag_chain = get_rag_chain_session(qa_chain,get_session = get_session_history)
        await invoke_save(rag_chain,'1','human','你是有什么问题')
    asyncio.run(main())


