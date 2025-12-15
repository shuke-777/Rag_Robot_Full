import asyncio

from v2_rag_with_stream_async import *
from rag_with_SQLALchemy_table import *
import rag_with_SQLALchemy_table
from Sql_base import *
url = 'mysql+aiomysql://shuke:123456@localhost/sk_db?charset=utf8mb4'
engine = create_async_engine(url, echo=True)
print(engine)
#初始化asyncsessionlocal
rag_with_SQLALchemy_table.AsyncSessionLocal=async_sessionmaker(bind = engine,class_=AsyncSession)
#测试保存信息
async def test_save():
    await db_save_message(session_id="test001", role="human",
                          content="你是什么模型")
    await db_save_message(session_id="test001", role="ai",
                          content="你好，有什么可以帮助你的？")
    await db_save_message(session_id="test001", role="human",
                          content="今天天气怎么样")
    print('对话保存成功')
async def test_load():
    history = await db_load_history(session_id="test001")
    print('加载到的数据量: ',len(history.messages))
    for msg in history.messages:
        print(f'{type(msg).__name__}:{msg.content}')
def main_test():
    local_embed = load_vector_store("1201Faiss.faiss")
    retrieval = local_embed.as_retriever(search_kwargs={'k': 3})
async def test_load1():
    await test_load()
    await engine.dispose()
async def test_save1():
    await test_save()
    await engine.dispose()
if __name__ == '__main__':
    asyncio.run(test_save1())