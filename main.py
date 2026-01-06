import asyncio
import sys
sys.path.append('src')
sys.path.append('kb')
sys.path.append('db')
sys.path.append('config')
from v2_rag_with_stream_async import create_history_aware_retriever_chain, create_qa_chain
from rag_kb_management import KnowledgeService,KnowledgeBaseManager,DocumentProcessor
from v3_rerank_rag_private import SimpleRerank
from typing import Optional
from rag_config import rerank_url,get_device,llm,_rerank_model
from rag_with_async_table import invoke_save,engine,get_rag_chain_session,get_session_history
from contextlib import asynccontextmanager
class RAGApplication:
    def __init__(self,kb_path:str,kb_name:str,use_rerank:bool = True):
        self.kb_path = kb_path
        self.kb_name = kb_name
        self.use_rerank = use_rerank

        self.knowledge_service :Optional[KnowledgeService] = None
        self.vector_store = None
        self.retriever = None
        self.rerank_model = None
        self.rag_chain = None

        self.is_initialized = False
        self.device =get_device()

        print(f"[RAGApplication] 初始化配置完成")
        print(f"  - 知识库: {kb_name}")
        print(f"  - Rerank: {'启用' if use_rerank else '禁用'}")
        print(f"  - 设备: {self.device}")
    async def startup(self):
        if self.is_initialized:
            print('[RAGApplication] 已经初始化过了')
            return
        print('RAG流程启动')
        self.knowledge_service = await asyncio.to_thread(
            self._load_knowledge_service
        )
        print('知识库服务初始化完成')
        self.vector_store =await asyncio.to_thread(
            self.knowledge_service.search_kb,self.kb_name
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={'k': 3})

        if self.use_rerank:
            print(f'正在加载rerank模型')
            self.rerank_model = await asyncio.to_thread(
                self._load_rerank_model)
            print('rerank模型加载完成')
            final_retriever = self.rerank_model
        else:
            print('未使用rerank模型，只使用retriever')
            final_retriever = self.retriever

        print('正在初始化RAG链')
        history_aware_retriever = create_history_aware_retriever_chain(
            llm=llm,
            retriever=final_retriever
        )
        qa_chain = create_qa_chain(
            llm=llm,
            history_aware_retriever=history_aware_retriever
        )
        self.rag_chain = get_rag_chain_session(
            rag_chain=qa_chain,
            get_session=get_session_history
        )
        print('RAG链初始化完成')
        self.is_initialized = True

    def _load_knowledge_service(self):
        return KnowledgeService(
            KnowledgeBaseManager(kb_path_or_name = self.kb_path),
                                 document_processor=DocumentProcessor())

    def _load_rerank_model(self):
        return SimpleRerank(
            model_name_or_path=rerank_url,
            base_retriever=self.retriever
        )
    async def chat_stream(self,session_id:str):
        if not self.is_initialized:
            raise RuntimeError('请先启动RAG应用')
        await invoke_save(session_id,rag=self.rag_chain)

    async def shutdown(self):
        if not self.is_initialized:
            return
        if engine:
            print('正在关闭数据库连接')
            await engine.dispose()
            print('数据库连接池已经关闭')
        self.vector_store = None
        self.retriever = None
        self.rerank_model = None
        self.rag_chain = None
        self.is_initialized = False
    @asynccontextmanager
    async def lifespan(self):
        await self.startup()
        try:
            yield self
        finally:
            await self.shutdown()
if __name__ == '__main__':
    from config.path_config import KB_LIST_DIR
    #kb_path: str, kb_name: str, use_rerank: bool = True
    kb_path = str(KB_LIST_DIR)
    kb_name = 'private_kb'
    app = RAGApplication(
        kb_path=kb_path,
        kb_name=kb_name,
        use_rerank=False
    )
    """
    stream聊天
    """
    async def example_stream():
        async with app.lifespan():
            await app.chat_stream('session_14301')
            print('聊天结束')
    asyncio.run(example_stream())

#
# def get_rerank_instance(retriever):
#     global _rerank_model
#     if _rerank_model is None:
#         print('首次初始化Rerank模型')
#         _rerank_model = SimpleRerank(model_name_or_path =rerank_url,
#                               base_retriever=retriever
#                               )
#         return _rerank_model
#
#
# async def main(kb_path,
#                kb_name,
#                session_id:str,
#                _rerank= True):
#     ks = KnowledgeService(
#         KnowledgeBaseManager(kb_path_or_name=kb_path), document_processor=DocumentProcessor())
#     vector_store=ks.search_kb(kb_name)
#     retriever = vector_store.as_retriever(search_kwargs={'k': 3})
#     if _rerank:
#         #rerank = SimpleRerank(model_name_or_path =rerank_url,
#                               #base_retriever=retriever
#                               #)
#         _rerank=get_rerank_instance(retriever)
#         history_aware_retriever=create_history_aware_retriever_chain(llm = llm, retriever=_rerank)
#         qa_chain = create_qa_chain( llm = llm,history_aware_retriever = history_aware_retriever)
#         qa_chain = get_rag_chain_session(rag_chain=qa_chain,get_session=get_session_history)
#         await invoke_save(session_id,rag=qa_chain)
#         await engine.dispose()


# if __name__ == '__main__':
#     from config.path_config import KB_LIST_DIR
#     kb_path_or_name = str(KB_LIST_DIR)
#     asyncio.run(main(kb_path=kb_path_or_name,kb_name = '技术文档',session_id = 'test12'))
