import asyncio
from v2_rag_with_stream_async import *
from rag_kb_management import KnowledgeService,KnowledgeBaseManager,DocumentProcessor
from v3_rerank_rag_private import SimpleRerank
from typing import Optional
from rag_config import rerank_url,get_device,llm
from rag_with_async_table import invoke_save,engine,get_rag_chain_session
device = get_device()
async def main(kb_path,
               kb_name,
               session_id:str,
               _rerank= True):
    ks = KnowledgeService(
        KnowledgeBaseManager(kb_path_or_name=kb_path), document_processor=DocumentProcessor())
    vector_store=ks.search_kb(kb_name)
    retriever = vector_store.as_retriever(search_kwargs={'k': 3})
    if _rerank:
        rerank = SimpleRerank(model_name_or_path =rerank_url,
                              base_retriever=retriever
                              )
        history_aware_retriever=create_history_aware_retriever_chain(llm = llm, retriever=rerank)
        qa_chain = create_qa_chain( llm = llm,history_aware_retriever = history_aware_retriever)
        qa_chain = get_rag_chain_session(rag_chain=qa_chain,get_session=get_session_history)
        await invoke_save('test1',rag=qa_chain)
        await engine.dispose()


if __name__ == '__main__':
    kb_path_or_name = '/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/kb_list'
    asyncio.run(main(kb_path=kb_path_or_name,kb_name = '技术文档',session_id = 'test12'))