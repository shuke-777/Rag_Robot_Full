from pathlib import Path

import numpy as np

from config import  get_device
from sentence_transformers import CrossEncoder
from v2_rag_with_stream_async import load_vector_store
class SimpleRerank:
    def __init__(self,model_name_or_path:str,
                 max_length:int = 512):
        self.device = get_device()
        print(f'已经加载到rerank模型:{model_name_or_path}')
        self.model = CrossEncoder(
            model_name_or_path=model_name_or_path,
            max_length=max_length,
            device = self.device
        )
    def _rerank(self,query,documents:list[str],top_k :int = 3):
        if not documents:
            return [],[]
        result = [[query,doc.page_content] for doc in documents]
        score = self.model.predict(result)
        top_k = min(top_k,len(documents))
        #这里先排序出来，然后用[::-1]就是从大到小来进行排序，取出来top_k个数值
        sorted_indices = np.argsort( score)[::-1][:top_k]
        rerank_docs = [documents[i]for i in sorted_indices]
        rerank_scores = [ float(score[i]) for i in sorted_indices]
        return rerank_docs,rerank_scores,sorted_indices.tolist()

if __name__ == '__main__':
    query = "什么是工具函数？"
    documents = [
        "工具函数是一种用于执行特定任务的辅助函数，通常被多个模块复用。",
        "Python 是一种高级编程语言，广泛应用于 Web 开发和数据科学。",
        "装饰器是 Python 中的一种设计模式，用于在不修改函数代码的情况下增强其功能。",
        "工具函数可以提高代码的可维护性和复用性，减少重复代码。",
        "机器学习是人工智能的一个分支，专注于让计算机从数据中学习。"
    ]
    vector  = load_vector_store("1201Faiss.faiss")
    retrieval = vector.as_retriever(search_kwargs={'k': 5})

    # 使用 invoke() 方法（LangChain 新版本推荐）
    query = '解析木怎么选择'
    result_i = [result for result in retrieval.invoke(query)]
    sentence_pairs = [[query, doc] for doc in result_i]
    #for i in sentence_pairs:
        #print(i)
    model_name = '/Users/salutethedawn/Desktop/model/bge-reranker-large'
    Rerank=SimpleRerank(model_name_or_path=model_name,max_length=512)
    result = Rerank._rerank(query, documents=result_i, top_k=3)
    rerank_docs, rerank_scores, indices = result
    for doc, score,indices_i,in zip(rerank_docs, rerank_scores,indices):
        print(f"分数: {score:.4f}, 内容: {doc.page_content},原始文档索引:{indices_i}")

