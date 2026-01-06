"""
简单的评估 CLI，演示如何通过命令行参数触发完整的数据集评估。

示例：
    python evaluation/cli.py \
        --vector-store /path/to/vector_store \
        --data /path/to/test_dataset.jsonl \
        --output-json /tmp/result.json \
        --output-md /tmp/result.md
"""

from __future__ import annotations

import sys
from pathlib import Path as _Path

# 将项目根目录添加到 Python 路径中
# cli.py 在 evaluation/ 目录下，项目根目录在其父目录
project_root = _Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import argparse
from pathlib import Path
from typing import Dict

from evl_full_private import FullEvaluator,EvaluateMetrics


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="JSONL 测试集运行完整的检索评估",
        #这里就是可以把传入的args给显示出来
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--vector-store",
        required=True,
        type=Path,
        help="FAISS 向量库目录（会传入 CompleteEvaluator）",
    )
    parser.add_argument(
        "--embedding-model",
        default="BAAI/bge-small-zh-v1.5",
        help="HuggingFace Embedding 模型名称",
    )
    parser.add_argument(
        "--data",
        required=True,
        type=Path,
        help="评估所用的 JSONL 测试集路径",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="可选：将完整评估结果（summary+details）保存为 JSON",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="可选：额外生成 Markdown 报告，仅包含指标摘要",
    )
    return parser.parse_args()


def write_markdown(summary: Dict[str, float], output_path: Path) -> None:
    """将指标摘要渲染为简单 Markdown 结果表。"""
    lines = [
        "# 评估结果摘要",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
    ]
    for metric, value in summary.items():
        lines.append(f"| {metric} | {value:.4f} |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    #这里写的是expanduser(),主要就是为了在写路径的时候，可以跨平台使用
    vector_store_path = str(args.vector_store.expanduser())
    test_data_path = str(args.data.expanduser())
    output_json = str(args.output_json.expanduser()) if args.output_json else None

    evaluator = FullEvaluator(
        vector_store=vector_store_path,
        embedding_model_name=args.embedding_model,
    )

    avg_metrics = evaluator .evl_dataset(
        dataset=test_data_path,
        output=output_json,
    )

    if args.output_md:
        write_markdown(avg_metrics, args.output_md.expanduser())

    print("\n关键指标：")
    for metric, value in avg_metrics.items():
        print(f"  {metric:15s}: {value:.4f}")

if __name__ == "__main__":
    main()
