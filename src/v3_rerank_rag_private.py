from typing import Any

import numpy as np
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output

from config import get_device
from sentence_transformers import CrossEncoder
class SimpleRerank(Runnable):
    def __init__(self,model_name_or_path:str,
                 max_length:int =512,
                 base_retriever = None,
                 initial_k:int =10,
                 final_k :int = 3):
        self.device = get_device()
        print(f'使用设备{self.device}')
        print(f'已经加载到rerank模型:{model_name_or_path}')
        self.model = CrossEncoder(
            model_name_or_path=model_name_or_path,
            max_length=max_length,
            device = self.device)
        self.base_retriever = base_retriever
        self.final_k = final_k
    def _rerank(self,document_list:list[str],query):
        try:
            if not document_list:
                return [],[],[]
            result = [[query,getattr(doc_i,'page_content',doc_i) ]for doc_i in  document_list]
            print(result)
            score = self.model.predict(result)
            print(score)
            score_k = min(self.final_k,len(document_list))
            #[1 4 2 3 0]就是从低到高来进行排序，这里显示的是下标
            sort_indices = np.argsort(score)[::-1][:score_k]
            print(sort_indices)
            rerank_docs = [document_list[i]for i in sort_indices]
            rerank_score = [score[i]for i in sort_indices]
            return rerank_docs,rerank_score,sort_indices

        except Exception as e:
            print(f'rerank发生错误{e}')
    def invoke(self,query :str ,config = None,**kwargs):
       try:
           if self.base_retriever:
               result = self.base_retriever.invoke(query)
           else:
               print('请先设置retriever')
               result = []
       except Exception as e:
           print(f'retriever发生错误{e}')
       rerank_docs,rerank_score,sort_indices = self._rerank(document_list=result,query= query)
       for doc,score,indices in zip(rerank_docs,rerank_score,sort_indices):
           print(f'{indices} {score:.3f} {doc}')
           doc.metadata['score'] = score
           doc.metadata['indices'] = indices
       return rerank_docs
    async def ainvoke(self, query:str):
        if self.base_retriever is None:
            #这里直接error并且退出，可以直接用logging 来打印错误信息
            raise ValueError("请先设置retriever")
        if hasattr(self.base_retriever,'ainvoke'):
            docs = await self.base_retriever.ainvoke(query)
        else:
            print('async用不了了，只能先用invoke了')
            docs = self.base_retriever.invoke(query)
        if not docs:
            return []
        rerank_docs,rerank_score,sort_indices=self._rerank(docs,query=query)
        for doc, score, indices in zip(rerank_docs, rerank_score, sort_indices):
            print(f'{indices} {score:.3f} {doc}')
            doc.metadata['score'] = score
            doc.metadata['indices'] = indices
        return rerank_docs




if __name__ == '__main__':
    query = "什么是工具函数？"
    documents = [
        "工具函数是一种用于执行特定任务的辅助函数，通常被多个模块复用。",
        "Python 是一种高级编程语言，广泛应用于 Web 开发和数据科学。",
        "装饰器是 Python 中的一种设计模式，用于在不修改函数代码的情况下增强其功能。",
        "工具函数可以提高代码的可维护性和复用性，减少重复代码。",
        "机器学习是人工智能的一个分支，专注于让计算机从数据中学习。"
    ]
    model_name = '/Users/salutethedawn/Desktop/model/bge-reranker-large'
    SimpleRerank = SimpleRerank(model_name_or_path=model_name)
    SimpleRerank._rerank(documents,query)