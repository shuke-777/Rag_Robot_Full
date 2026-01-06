import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
import uuid
from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'src'))
sys.path.append(str(project_root / 'kb'))
sys.path.append(str(project_root / 'db'))
sys.path.append(str(project_root / 'config'))
from main import RAGApplication
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from rag_config import llm, ZHIPUEmbeddings
from tqdm import tqdm
class RagEvaluator:
    def __init__(self,kb_path:str,kb_name:str,use_rerank:bool = True):
        self.kb_path = kb_path
        self.kb_name = kb_name
        self.use_rerank = use_rerank
        self.app = None
    async def generate_answer(self,test_dataset_path):
        with open(test_dataset_path,'r',encoding='utf-8') as f:
            test_dataset = json.load(f)
        print('数据长度:',len(test_dataset))
        print(f"是否使用rerank:{'启用rerank'if self.use_rerank else '禁用rerank'}")
        result = []
        self.app = RAGApplication(
            kb_path=self.kb_path,
            kb_name=self.kb_name,
            use_rerank=self.use_rerank
        )
        async with self.app.lifespan():
            test_dataset =test_dataset[:1]
            pbar = tqdm(enumerate(test_dataset), total=len(test_dataset), desc='生成答案中')
            for i, item in pbar:
                question = item['question']
                ground_truth = item['ground_truth']
                tqdm.write(f'[{i}/{len(test_dataset)}]问题:{question}')
                try:
                    if self.use_rerank:
                        retrieved_docs = await self.app.rerank_model.ainvoke(question)
                    else:
                        retriever = self.app.retriever
                        retrieved_docs = await asyncio.to_thread(
                        retriever.invoke,question
                    )

                    contexts = [doc.page_content for doc in retrieved_docs]
                    response = await self.app.rag_chain.ainvoke(
                        {
                         'input':question
                        },config={'configurable':{'session_id':str(uuid.uuid4())}}
                    )
                    answer = response
                    tqdm.write(f'答案:{answer[:100]}')
                    tqdm.write(f'检索到{len(contexts)}个文档\n')
                    result.append({'question':question,
                                   'answer':answer,
                                   'contexts': contexts,
                                   'ground_truth':ground_truth})
                except Exception as e:
                    tqdm.write(f'错误:{str(e)}')
                    result.append(
                        {'question':question,
                         'answer':'',
                         'contexts':[],
                         'ground_truth':ground_truth}
                    )
        return result
    def run_evaluation(self,results:list,output_path:str = None):
        print('开始评估')
        dataset = Dataset.from_dict({
            'question': [r['question'] for r in results],
            'answer': [r['answer'] for r in results],
            'contexts': [r['contexts'] for r in results],
            'ground_truth': [r['ground_truth'] for r in results]
        })
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
        eval_result = evaluate(dataset, metrics=metrics, llm=llm, embeddings=ZHIPUEmbeddings)
        self._print_results(eval_result)
        if output_path:
            self._save_results(eval_result=eval_result,
                               src_result=results,
                               output_path = output_path)
    def _print_results(self, eval_results):
        """打印评估结果"""
        print(f"\n{'=' * 60}")
        print("评估结果")
        print(f"{'=' * 60}\n")

        print("📊 综合指标:")
        # 处理可能是列表的情况
        faithfulness_val = eval_results['faithfulness']
        if isinstance(faithfulness_val, list):
            faithfulness_val = sum(faithfulness_val) / len(faithfulness_val) if faithfulness_val else 0

        answer_relevancy_val = eval_results['answer_relevancy']
        if isinstance(answer_relevancy_val, list):
            answer_relevancy_val = sum(answer_relevancy_val) / len(answer_relevancy_val) if answer_relevancy_val else 0

        context_precision_val = eval_results['context_precision']
        if isinstance(context_precision_val, list):
            context_precision_val = sum(context_precision_val) / len(context_precision_val) if context_precision_val else 0

        context_recall_val = eval_results['context_recall']
        if isinstance(context_recall_val, list):
            context_recall_val = sum(context_recall_val) / len(context_recall_val) if context_recall_val else 0

        print(f"  Faithfulness (忠实度):         {faithfulness_val:.4f}")
        print(f"  Answer Relevancy (答案相关性): {answer_relevancy_val:.4f}")
        print(f"  Context Precision (上下文精确): {context_precision_val:.4f}")
        print(f"  Context Recall (上下文召回):    {context_recall_val:.4f}")
        print(f"\n{'=' * 60}")
    def _save_results(self,eval_result,src_result,output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 处理可能是列表的评估结果
        def get_avg(val):
            if isinstance(val, list):
                return sum(val) / len(val) if val else 0
            return float(val)

        summary = {
            'timestamp':timestamp,
            'config':
                {
                    'kb_name':self.kb_name,
                    'use_rerank':self.use_rerank
                },
            'metrics':
                {
                    'Faithfulness': get_avg(eval_result['faithfulness']),
                    'Answer Relevancy': get_avg(eval_result['answer_relevancy']),
                    'Context Precision': get_avg(eval_result['context_precision']),
                    'Context Recall': get_avg(eval_result['context_recall'])
                }
        }

        # 确保输出目录存在
        Path(output_path).mkdir(parents=True, exist_ok=True)

        summary_path = Path(output_path)/f'summary_{timestamp}.json'
        with open(summary_path,'w',encoding='utf-8') as f:
            json.dump(summary,f,indent=2,ensure_ascii=False)
        detail_path = Path(output_path)/f'detail_{timestamp}.json'
        with open(detail_path,'w',encoding='utf-8') as f:
            json.dump(src_result,f,indent=2,ensure_ascii=False)
        print(f'summary已经保存完成，路径是{summary_path}\n')
        print(f'detail已经保存完成，路径是{detail_path}\n')

if __name__ == '__main__':
    dataset_path = str(TEST_DATASET_PATH)
    kb_path = str(KB_LIST_DIR)
    kb_name = 'private_kb'
    RAG = RagEvaluator(
        kb_path = kb_path,
        kb_name = kb_name,
        use_rerank = True
    )
    output_path =str(EVALUATION_RESULTS_DIR)
    result = asyncio.run(RAG.generate_answer(dataset_path))
    RAG.run_evaluation(result,output_path)
