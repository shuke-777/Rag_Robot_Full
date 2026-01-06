import os
from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
import json
import time
from pathlib import Path

# 添加项目路径，确保能导入其他模块
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
sys.path.append(str(project_root / 'config'))
sys.path.append(str(project_root / 'src'))
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from datasets import Dataset
from ragas import evaluate
from ragas.metrics.collections import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from rag_config import ZHIPUEmbeddings, client, zhipu_reranker
import pprint
import tqdm
from sentence_transformers import CrossEncoder
from src.v3_rerank_rag_private import SimpleRerank
#指标
class EvaluateMetrics:
    @staticmethod
    def recall_k(retrieved_ids:list[str],relevant_ids:list[str],k:int):
        if not relevant_ids:
            return 0.0
        retrieved_set = set(retrieved_ids[:k])
        relevant_ids = set(relevant_ids)
        hits = len(retrieved_set&relevant_ids)
        return hits/len(relevant_ids)

    @staticmethod
    def precision_k(retrieved_ids:list[str],relevant_ids:list[str],k:int):
        if k == 0:
            return 0.0
        retrieved_set = set(retrieved_ids[:k])
        relevant_ids = set(relevant_ids)
        hits = len(retrieved_set & relevant_ids)
        return hits / k
    @staticmethod
    def mrr(retrieved_ids:list[str],relevant_ids:list[str]):
        relevant_ids = set(relevant_ids)
        for i,doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                return 1.0 / (i+1)
        return 0.0
from config.rag_config import get_device,rerank_url

class FullEvaluator:
    def __init__(self,vector_store:str,embedding_model_name:None,rerank_model_name:str,
                 use_rerank : bool):
        print('初始化评估器')
        self.embedding = ZHIPUEmbeddings
        self.use_rerank = use_rerank
        self.vector_store = FAISS.load_local(vector_store,self.embedding,allow_dangerous_deserialization=True)
        if self.use_rerank:
            base_retriever = self.vector_store.as_retriever(search_kwargs={'k': 20})

            self.rerank_model = SimpleRerank(
                base_retriever=base_retriever,
                reranker=CrossEncoder(rerank_model_name,device=get_device())
            )
        print('向量库加载完成')
        if use_rerank:
            print('✅ 使用智谱在线 Rerank 模型')

    def retrieve_doc(self,query:str,k:int):
        if self.use_rerank:
          docs = SimpleRerank.invoke(query)
        else:
            docs = self.vector_store.similarity_search(query,k=k)
        retrieved_ids = [doc.metadata.get('id','')for doc in docs]
        context = [doc.page_content for doc in docs]
        return retrieved_ids,context

    def compute_retrieval(self,query,relevant_doc,
                       k:list[int]):
        retrieved_ids,context = self.retrieve_doc(query,k=max(k))
        metrics = {}
        for k_list in k:
            metrics[f'recall@{k_list}'] = EvaluateMetrics.recall_k(
                retrieved_ids = retrieved_ids,
                relevant_ids=relevant_doc,
                k = k_list
            )
            metrics[f'precision@{k_list}'] = EvaluateMetrics.precision_k(
                retrieved_ids = retrieved_ids,
                relevant_ids=relevant_doc,
                k = k_list
            )
            metrics[f'mrr'] = EvaluateMetrics.mrr(
                retrieved_ids = retrieved_ids,
                relevant_ids=relevant_doc
            )
        return  metrics
    def evaluate_single_question(self,query,relevant_doc,k_list:list[int]):
        start_time = time.time()
        retrieved_ids,context=self.retrieve_doc(query, k = max(k_list))
        retrieval_time = time.time() - start_time
        #计算检索指标
        metrics=self.compute_retrieval(query = query,relevant_doc = relevant_doc,k = k_list)

        #end2end_metrics
        end2end_metrics = {
            'retrieval_time':retrieval_time,
            'num_retrieved':len(retrieved_ids),
        }
        result = {
            'question':query,
            'retrieved_ids':retrieved_ids,
            'contexts':context,
            'retrieval_metrics':metrics,
            'end2end_metrics':end2end_metrics
        }
        return result
    def evl_dataset(self,dataset,output) -> dict[str,dict]:
        print(f'开始评估数据集:{dataset}')
        with open(str(dataset),'r',encoding='utf-8') as f:
            full_test_dataset = json.load(f)
        dataset_list = []
        for line in full_test_dataset:
            dataset_list.append(line)
        print(f'数据总长度{len(dataset_list)}')
        all_result = []
        all_metrics = {
            'recall@3': [],
            'recall@5': [],
            'precision@3': [],
            'precision@10':[],
            'mrr': [],
            'retrieval_time': []
        }
        tqdm1 = tqdm.tqdm(enumerate(dataset_list),total=len(dataset_list),desc='评估进度')
        for i,item in tqdm1:
            result = self.evaluate_single_question(
                query = item['question'],
                relevant_doc = item['relevant_docs'],
                k_list = [3,5,10]
            )
            all_result.append(result)
            for metrics_name in ['recall@3','recall@5','precision@3','mrr','precision@10']:
                all_metrics[metrics_name].append(result['retrieval_metrics'][metrics_name])
            all_metrics['retrieval_time'].append(result['end2end_metrics']['retrieval_time'])

        avg_metrics = {
            metrics_name: sum(values)/len(values) for metrics_name,values in all_metrics.items()
        }
        save_content = {
            'avg': avg_metrics,
            'detail': all_metrics
        }
        with open(output,'w',encoding='utf-8') as f:
            json.dump(save_content,f,ensure_ascii=False,indent=4)
        print(f'结果已经保存到了{output}')
        return avg_metrics


if __name__ == '__main__':
    rerank_model = BGE_RERANKER_MODEL
    vector_store = str(PRIVATE_KB_VECTOR)
    FullEvl=FullEvaluator(vector_store,embedding_model_name=ZHIPUEmbeddings,
                          rerank_model_name=rerank_model,use_rerank=True)
    print(FullEvl.rerank_model)
    # with open('test_dataset_annotated.json','r',encoding='utf-8') as f:
    #     test_dataset = json.load(f)
    #query = test_dataset[0]['question']
    #pprint.pprint(FullEvl.evaluate_single_question(query, relevant_doc=test_dataset[0]['relevant_docs'], k_list=[3,5]))
    # dataset = Path('test_dataset_annotated.json')
    # output = EVALUATION_RESULTS_DIR / 'full_evl_result' / 'evl1230_1.json'
    #
    # FullEvl.evl_dataset(dataset=dataset,output = output)




