"""
这里增加功能:
- 一个是save_history(先放到内存中，再放到sql中)，
- 一个是load_history，如果在内存中没有session_id的话，就从sql中取出来
- 一个是要集成在input中来做，实现可持续存储，而不是单一信息的存储,并且要包在一个func内
这里就是也是都要用async来做

"""
import asyncio

from Sql_base import base
from rag_with_SQLALchemy_table import Session,Messages
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy import select,inspect
from contextlib import asynccontextmanager
from Sql_base import MessagesTableNew,SessionTable
from langchain_core.chat_history import AIMessage,HumanMessage,BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from v2_rag_with_stream_async import llm, load_vector_store,create_history_aware_retriever_chain, create_qa_chain,RunnableWithMessageHistory
db_url = 'mysql+aiomysql://shuke:123456@localhost/sk_db?charset=utf8mb4'
engine = create_async_engine(url = db_url)
async_session = async_sessionmaker(bind=engine)

@asynccontextmanager
async def get_async_db():
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()

table= list(base.metadata.tables.keys())
print(table)
session_table_new = table[3]
message_table_new = table[4]

async def save_history_db(session_id:str,content:str,role:str):
    async with get_async_db() as db:
        try:
            query_content = select(SessionTable).where(SessionTable.session_id == session_id)
            session_result = await db.execute(query_content)
            session_result = session_result.scalar_one_or_none()
            if not session_result:
                session1 = SessionTable(session_id = session_id)
                #这个方法不是async
                db.add(session1)
                await db.commit ()
                await db.refresh(session1)
                session_result = session1
            message_add_content = MessagesTableNew(content =content,role = role,session_id = session_result.id)
            db.add(message_add_content)
            await db.commit()
            print('数据保存成功')

        except Exception as e:
            await db.rollback()
            print(f'数据库保存失败{e}')

async def load_db_history(session_id:str):
    async with get_async_db() as db:
        # ✅ 修改1: 使用 ChatMessageHistory 替代 AsyncChatMessageHistory
        load_history = ChatMessageHistory()
        query_content = select(SessionTable).where(SessionTable.session_id == session_id)
        result = await db.execute(query_content)
        result = result.scalar_one_or_none()
        if result:
            query1 = select(MessagesTableNew).where(MessagesTableNew.session_id == result.id)
            result2 = await (db.execute(query1))
            result2 = result2.scalars().all()
            for result_i in result2:
                if result_i.role =='ai':
                    load_history.add_ai_message(AIMessage(content = result_i.content))
                else:
                    load_history.add_user_message(HumanMessage(content = result_i.content))
    return load_history

store = {}

# ✅ 修改2: 将 async def 改为 def（同步函数）
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        print(f'[警告] session {session_id} 未在缓存中，返回空历史')
        store[session_id] = ChatMessageHistory()
    #else:
        #print(f'[缓存命中] session:{session_id}')
    return store[session_id]


async def invoke_save(session_id:str,rag):
    # ✅ 修改4: 在对话循环开始前，预加载历史到缓存
    if session_id not in store:
        print(f'[预加载] 从数据库加载 session:{session_id}')
        store[session_id] = await load_db_history(session_id)
        print(f'[预加载完成] 已加载 {len(store[session_id].messages)} 条历史消息')

    while True:
        full_response = ""
        try:
            query = await asyncio.to_thread(input,'[Human]')
            if query.lower() == 'exit':
                print('886')
                return
            #await save_history_db(session_id,query,'human')
            print(f'[AI回复]:',end='',flush=True)
            result = rag.astream({'input':query},
                              config = {'configurable':{'session_id' : session_id}})
            async for chunk in result:
                print(chunk,end='',flush=True)
                full_response += chunk
            print()
            #这里就是用最后两条来取出来
            #这里为什么用messages，因为这里是用了chat_history里面的BaseChatMessageHistory,
            #messages都是存储在messages里面的
            messages = store[session_id].messages[-2:]
            for msg in messages:
                role ='ai' if isinstance(msg,AIMessage) else 'human'
                await save_history_db(session_id,msg.content,role)
        except Exception as e:
            print(f'[错误]保存数据失败{e}')


def get_rag_chain_session(rag_chain,get_session):
    """创建带历史管理的RAG链"""
    rag_chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session,
        input_messages_key='input',
        history_messages_key='chat_history',
    )
    return rag_chain_with_history


async def main():
    #async with get_async_db() as db:
    await invoke_save('test2',rag_chain)
    await engine.dispose()



if __name__ == '__main__':
    local_store = '/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/vector_store/1201Faiss.faiss'
    embed = load_vector_store(local_store)
    retriever = embed.as_retriever(search_kwargs={'k': 3})
    retriever_chain = create_history_aware_retriever_chain(llm=llm, retriever=retriever)
    qa_chain = create_qa_chain(llm=llm, history_aware_retriever=retriever_chain)
    rag_chain = get_rag_chain_session(qa_chain, get_session=get_session_history)
    asyncio.run(main())