from __future__ import annotations
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.absolute()
#print(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 添加 config 和 src 目录到路径，解决 v3_rerank_rag_private.py 的导入问题
sys.path.append(str(project_root / 'config'))
sys.path.append(str(project_root / 'src'))

import argparse
from evl_full_private import EvaluateMetrics,FullEvaluator
from config.rag_config import ZHIPUEmbeddings

def parse_args():
    parser = argparse.ArgumentParser(
        description='测试集运行完整的检索评估',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--vector',
        type = Path,
        help='向量数据路径',
        default=project_root / 'kb/kb_list/Controlled_chunk_250/vector_store'
    )
    parser.add_argument(
        '--dataset',
        type = Path,
        help='测试集路径',
        default=project_root / 'evaluation/test_dataset_annotated.json'
    )
    parser.add_argument(
        '--output',
        type = Path,
        help = '输出路径',
        default=project_root / 'evaluation/results/chunk250/no_rerank.json'
    )
    parser.add_argument(
        '--rerank',
        action='store_true',
        help='是否使用rerank模型进行rerank'
    )
    return parser.parse_args()

def write_output(output_path:Path,summary:dict[str,float]):
    output_path.parent.mkdir(parents=True,exist_ok=True)
    for metric,value in summary.items():
        output_path.write_text(f'{metric}:{value:.4f}')
    print('写入已经完成')

def main():
    args = parse_args()
    vector_store = str(args.vector.expanduser().absolute())
    dataset = str(args.dataset.expanduser().absolute())
    output = str(args.output.expanduser().absolute()) if args.output else None
    evaluator = FullEvaluator(
        vector_store= vector_store,
        embedding_model_name=ZHIPUEmbeddings,
        rerank_model_name=args.rerank,
        use_rerank=args.rerank
    )
    avg_metrics=evaluator.evl_dataset(
        dataset = dataset,
        output = output
    )
    print('已经写入完成了')

if __name__ == '__main__':
    main()