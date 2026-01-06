"""
完整RAG系统评估脚本
整合了：检索评估、生成评估(ragas)、端到端评估
"""

import json
import time
from typing import List, Dict, Any
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# ========================================
# 第一部分: 检索评估指标
# ========================================

class RetrievalMetrics:
    """计算检索相关的指标"""

    @staticmethod
    def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        """
        Recall@K: 前K个检索结果中,有多少相关文档被召回
        公式: Recall@K = |检索到的相关文档| / |所有相关文档|
        """
        if not relevant_ids:
            return 0.0

        retrieved_set = set(retrieved_ids[:k])
        relevant_set = set(relevant_ids)
        hits = len(retrieved_set & relevant_set)

        return hits / len(relevant_set)

    @staticmethod
    def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        """
        Precision@K: 前K个检索结果中,有多少是相关的
        公式: Precision@K = |检索到的相关文档| / K
        """
        if k == 0:
            return 0.0

        retrieved_set = set(retrieved_ids[:k])
        relevant_set = set(relevant_ids)
        hits = len(retrieved_set & relevant_set)

        return hits / k

    @staticmethod
    def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        """
        MRR (Mean Reciprocal Rank): 第一个相关文档的排名倒数
        公式: MRR = 1 / rank(第一个相关文档)
        """
        relevant_set = set(relevant_ids)

        for i, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant_set:
                return 1.0 / i

        return 0.0


# ========================================
# 第二部分: 完整评估器
# ========================================

class CompleteEvaluator:
    """整合检索、生成、端到端的完整评估器"""

    def __init__(
        self,
        vector_store_path: str,
        embedding_model_name: str = "BAAI/bge-small-zh-v1.5"
    ):
        """
        初始化评估器

        Args:
            vector_store_path: FAISS向量库路径
            embedding_model_name: embedding模型名称
        """
        print("🔧 初始化评估器...")

        # 加载embedding模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'}
        )

        # 加载向量库
        self.vector_store = FAISS.load_local(
            vector_store_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        print(f"✅ 向量库加载完成: {vector_store_path}")

    def retrieve_documents(self, query: str, k: int = 10) -> tuple:
        """
        检索文档并返回文档ID和内容

        Returns:
            (retrieved_ids, contexts): 文档ID列表和内容列表
        """
        # 检索文档
        docs = self.vector_store.similarity_search(query, k=k)

        # ✅ 从metadata提取文档ID
        retrieved_ids = [
            doc.metadata.get('id', '')
            for doc in docs
            if doc.metadata.get('id')
        ]

        # 提取文档内容（用于ragas评估）
        contexts = [doc.page_content for doc in docs]

        return retrieved_ids, contexts

    def compute_retrieval_metrics(
        self,
        retrieved_ids: List[str],
        relevant_docs: List[str],
        k_values: List[int]
    ) -> Dict[str, float]:
        """
        根据检索结果计算各项指标

        Args:
            retrieved_ids: 当前检索得到的文档ID
            relevant_docs: 标注的相关文档ID列表
            k_values: 要评估的K值列表

        Returns:
            指标字典
        """
        metrics = {}
        for k in k_values:
            metrics[f'recall@{k}'] = RetrievalMetrics.recall_at_k(
                retrieved_ids, relevant_docs, k
            )
            metrics[f'precision@{k}'] = RetrievalMetrics.precision_at_k(
                retrieved_ids, relevant_docs, k
            )

        metrics['mrr'] = RetrievalMetrics.mrr(retrieved_ids, relevant_docs)
        return metrics

    def evaluate_retrieval(
        self,
        query: str,
        relevant_docs: List[str],
        k_values: List[int] = [3, 5, 10]
    ) -> Dict[str, float]:
        """
        评估检索性能

        Args:
            query: 查询问题
            relevant_docs: 标注的相关文档ID列表
            k_values: 要评估的K值列表

        Returns:
            包含各项指标的字典
        """
        # 检索文档
        retrieved_ids, _ = self.retrieve_documents(query, k=max(k_values))

        # 计算各项指标
        return self.compute_retrieval_metrics(
            retrieved_ids=retrieved_ids,
            relevant_docs=relevant_docs,
            k_values=k_values
        )

    def evaluate_single_question(
        self,
        question: str,
        ground_truth: str,
        relevant_docs: List[str],
        k: int = 3
    ) -> Dict[str, Any]:
        """
        评估单个问题（检索 + 端到端）
        注意: 这里不包括ragas生成评估,因为需要实际的LLM答案

        Args:
            question: 问题
            ground_truth: 标准答案
            relevant_docs: 标注的相关文档ID
            k: 检索文档数量

        Returns:
            评估结果字典
        """
        # 1. 检索评估
        start_time = time.time()
        retrieved_ids, contexts = self.retrieve_documents(question, k=k)
        retrieval_time = time.time() - start_time

        # 计算检索指标
        retrieval_metrics = self.compute_retrieval_metrics(
            retrieved_ids=retrieved_ids,
            relevant_docs=relevant_docs,
            k_values=[3, 5]
        )

        # 2. 端到端指标
        end_to_end_metrics = {
            'retrieval_time': retrieval_time,
            'num_retrieved': len(retrieved_ids)
        }

        return {
            'question': question,
            'retrieved_ids': retrieved_ids,
            'contexts': contexts,  # 用于后续ragas评估
            'retrieval_metrics': retrieval_metrics,
            'end_to_end_metrics': end_to_end_metrics
        }

    def evaluate_dataset(
        self,
        test_data_path: str,
        output_path: str = None
    ) -> Dict[str, float]:
        """
        评估整个测试数据集

        Args:
            test_data_path: 测试数据集路径(JSONL格式)
            output_path: 结果保存路径(可选)

        Returns:
            平均指标字典
        """
        print(f"\n📊 开始评估数据集: {test_data_path}")

        # 加载测试数据
        test_data = []
        with open(test_data_path, 'r', encoding='utf-8') as f:
            for line in f:
                test_data.append(json.loads(line))

        print(f"共加载 {len(test_data)} 条测试数据")

        # 评估每个问题
        all_results = []
        all_metrics = {
            'recall@3': [],
            'recall@5': [],
            'precision@3': [],
            'mrr': [],
            'retrieval_time': []
        }

        for i, item in enumerate(test_data, 1):
            print(f"\n处理问题 {i}/{len(test_data)}: {item['question'][:50]}...")

            result = self.evaluate_single_question(
                question=item['question'],
                ground_truth=item.get('answer', ''),
                relevant_docs=item.get('relevant_docs', [])
            )

            all_results.append(result)

            # 收集指标
            for metric_name in ['recall@3', 'recall@5', 'precision@3', 'mrr']:
                all_metrics[metric_name].append(
                    result['retrieval_metrics'][metric_name]
                )
            all_metrics['retrieval_time'].append(
                result['end_to_end_metrics']['retrieval_time']
            )

            # 打印当前结果
            print(f"  Recall@3: {result['retrieval_metrics']['recall@3']:.3f}")
            print(f"  MRR: {result['retrieval_metrics']['mrr']:.3f}")

        # 计算平均指标
        avg_metrics = {
            metric_name: sum(values) / len(values)
            for metric_name, values in all_metrics.items()
        }

        # 打印总结
        print("\n" + "="*50)
        print("📈 评估结果总结")
        print("="*50)
        for metric_name, value in avg_metrics.items():
            print(f"{metric_name:20s}: {value:.4f}")

        # 保存结果
        if output_path:
            self._save_results(all_results, avg_metrics, output_path)

        return avg_metrics

    def _save_results(
        self,
        all_results: List[Dict],
        avg_metrics: Dict[str, float],
        output_path: str
    ):
        """保存评估结果到文件"""
        output_data = {
            'summary': avg_metrics,
            'details': all_results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {output_path}")


# ========================================
# 第三部分: Ragas评估(需要LLM生成答案)
# ========================================

class RagasEvaluator:
    """Ragas生成质量评估"""

    @staticmethod
    def prepare_ragas_dataset(evaluation_results: List[Dict]) -> Dataset:
        """
        将评估结果转换为ragas需要的格式

        注意: 这里假设evaluation_results中已经包含了LLM生成的答案
        """
        ragas_data = {
            'question': [],
            'answer': [],  # LLM生成的答案
            'contexts': [],
            'ground_truth': []
        }

        for result in evaluation_results:
            ragas_data['question'].append(result['question'])
            ragas_data['answer'].append(result.get('generated_answer', ''))  # 需要先生成
            ragas_data['contexts'].append(result['contexts'])
            ragas_data['ground_truth'].append(result.get('ground_truth', ''))

        return Dataset.from_dict(ragas_data)

    @staticmethod
    def evaluate_with_ragas(dataset: Dataset) -> Dict[str, float]:
        """
        使用ragas评估生成质量

        注意: 需要先生成答案,这里只是展示如何调用ragas
        """
        print("\n🤖 开始Ragas评估...")

        result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
        )

        return result


# ========================================
# 第四部分: 主函数示例
# ========================================

def main():
    """主评估流程"""

    # 配置路径
    # ⚠️  注意：这些是其他项目（毕业设计）的路径，请根据实际项目修改
    # 建议使用 config.path_config 中的路径配置
    VECTOR_STORE_PATH = "/Users/salutethedawn/Desktop/毕业设计/data/vector_stores/python_tutorial_knowledge_base"
    TEST_DATA_PATH = "/Users/salutethedawn/Desktop/毕业设计/data/test_dataset.jsonl"
    OUTPUT_PATH = "/Users/salutethedawn/Desktop/毕业设计/results/evaluation_results.json"

    # 当前项目的推荐配置（取消注释使用）：
    # from config.path_config import PRIVATE_KB_VECTOR, TEST_DATASET_PATH, EVALUATION_RESULTS_DIR
    # VECTOR_STORE_PATH = str(PRIVATE_KB_VECTOR)
    # TEST_DATA_PATH = str(TEST_DATASET_PATH)
    # OUTPUT_PATH = str(EVALUATION_RESULTS_DIR / "evaluation_results.json")

    # 创建评估器
    evaluator = CompleteEvaluator(
        vector_store_path=VECTOR_STORE_PATH,
        embedding_model_name="BAAI/bge-small-zh-v1.5"
    )

    # 方式1: 评估单个问题
    print("\n" + "="*50)
    print("示例1: 评估单个问题")
    print("="*50)

    single_result = evaluator.evaluate_single_question(
        question="什么是软件测试?",
        ground_truth="软件测试是...",
        relevant_docs=["15_软件测试基础_s1_c0", "15_软件测试基础_s1_c1"]
    )

    print(f"检索到的文档: {single_result['retrieved_ids'][:3]}")
    print(f"Recall@3: {single_result['retrieval_metrics']['recall@3']:.3f}")

    # 方式2: 评估整个数据集
    print("\n" + "="*50)
    print("示例2: 评估整个数据集")
    print("="*50)

    avg_metrics = evaluator.evaluate_dataset(
        test_data_path=TEST_DATA_PATH,
        output_path=OUTPUT_PATH
    )

    print("\n✅ 评估完成!")

    # 方式3: Ragas评估(需要先生成答案)
    # 这里只是示例,实际需要先调用LLM生成答案
    print("\n" + "="*50)
    print("提示: Ragas评估需要先生成答案")
    print("="*50)
    print("1. 使用evaluator.retrieve_documents()获取contexts")
    print("2. 调用LLM生成答案")
    print("3. 使用RagasEvaluator.evaluate_with_ragas()评估")


if __name__ == "__main__":
    main()
