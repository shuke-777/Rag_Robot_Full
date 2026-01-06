import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Optional
import torch
from langchain_community.embeddings import ZhipuAIEmbeddings
from zhipuai import ZhipuAI
from config.path_config import BGE_RERANKER_MODEL

load_dotenv()
# rerank_url - 使用统一路径配置
rerank_url = BGE_RERANKER_MODEL
# db_url
db_url = 'mysql+aiomysql://shuke:123456@localhost/sk_db?charset=utf8mb4'
_rerank_model = None
client = ZhipuAI(api_key=os.getenv('ZHIPUAI_API_KEY'))
llm = ChatOpenAI(
    model_name=os.getenv('ZHIPU_MODEL_NAME'),
    api_key=os.getenv('ZHIPUAI_API_KEY'),
    base_url=os.getenv('ZHIPUAI_URL')
)
ZHIPUEmbeddings =ZhipuAIEmbeddings(
            model_name='embedding-2',
            api_key=os.getenv('ZHIPUAI_API_KEY')
        )


class ZhipuReranker:

    def __init__(self, client: ZhipuAI, model: str = "glm-4-flash", top_n: int = 10):

        self.client = client
        self.model = model
        self.top_n = top_n

    def rerank(self, query: str, documents: list, top_n: Optional[int] = None) -> list:

        from langchain_core.documents import Document

        if not documents:
            return []

        # 判断输入是 Document 对象还是字符串
        is_document_list = isinstance(documents[0], Document)

        # 提取文本内容
        if is_document_list:
            texts = [doc.page_content for doc in documents]
        else:
            texts = documents

        # 调用智谱 rerank API
        try:
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=texts,
                top_n=top_n or self.top_n
            )

            # 解析返回结果
            reranked_results = []
            for item in response.results:
                idx = item.index  # 原始文档的索引
                score = item.relevance_score  # 相关性分数

                # 构造返回的 Document 对象
                if is_document_list:
                    doc = documents[idx]
                    # 添加 rerank 分数到 metadata
                    doc.metadata['rerank_score'] = score
                    reranked_results.append(doc)
                else:
                    # 如果输入是字符串，创建新的 Document 对象
                    doc = Document(
                        page_content=texts[idx],
                        metadata={'rerank_score': score}
                    )
                    reranked_results.append(doc)

            return reranked_results

        except Exception as e:
            print(f"❌ 智谱 Rerank 调用失败: {e}")
            # 失败时返回原始文档
            if is_document_list:
                return documents[:top_n or self.top_n]
            else:
                return [Document(page_content=text) for text in texts[:top_n or self.top_n]]

    def invoke(self, query: str, documents: list = None, top_n: Optional[int] = None):
        """
        兼容 LangChain 的 invoke 调用方式
        """
        if documents is None:
            documents = []
        return self.rerank(query, documents, top_n)


# 创建全局 reranker 实例
zhipu_reranker = ZhipuReranker(client=client, top_n=10)
#db_setting (moved to top)

#get_device
def get_device():
    """
    自动检测设备
    """
    if torch.cuda.is_available():
        device = 'cuda'
        print(f"🚀 检测到 NVIDIA GPU，将使用 CUDA 加速")
    elif torch.backends.mps.is_available():
        device = 'mps'
        print(f"🚀 检测到 Apple Silicon，将使用 MPS 加速")
    else:
        device = 'cpu'
        print(f"💻 将使用 CPU 运行")
    return device


if __name__ == '__main__':
    print(llm.invoke('你好'))

