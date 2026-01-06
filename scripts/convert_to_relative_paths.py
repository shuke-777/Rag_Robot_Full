"""
批量将绝对路径转换为相对路径的脚本
"""

import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要替换的路径映射
PATH_MAPPINGS = {
    # 知识库路径
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/kb_list": "str(KB_LIST_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/kb_list/private_kb/vector_store": "str(PRIVATE_KB_VECTOR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/kb_list/private_kb": "str(PRIVATE_KB_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/save_path": "str(KB_SAVE_PATH_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb/parse_result": "str(KB_PARSE_RESULT_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/kb": "str(KB_DIR)",

    # 数据路径
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/data/raw_data/documents": "str(DOCUMENTS_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/data/raw_data": "str(RAW_DATA_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/data": "str(DATA_DIR)",

    # 评估路径
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/evaluation/test_dataset.json": "str(TEST_DATASET_PATH)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/evaluation/results": "str(EVALUATION_RESULTS_DIR)",
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/evaluation": "str(EVALUATION_DIR)",

    # 向量存储路径
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/vector_store": "str(VECTOR_STORE_DIR)",

    # 数据库路径
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot/db": "str(DB_DIR)",

    # 项目根目录
    r"/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/rag-chatbot": "str(PROJECT_ROOT)",

    # 外部模型路径
    r"/Users/salutethedawn/Desktop/model/bge-reranker-large": "BGE_RERANKER_MODEL",
}

# 需要添加的 import 语句
REQUIRED_IMPORTS = """from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)"""


def convert_file(file_path: Path):
    """转换单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        needs_import = False

        # 替换路径（按长度降序，避免部分替换）
        sorted_mappings = sorted(PATH_MAPPINGS.items(), key=lambda x: len(x[0]), reverse=True)
        for old_path, new_path in sorted_mappings:
            if old_path in content:
                content = content.replace(f"'{old_path}'", new_path)
                content = content.replace(f'"{old_path}"', new_path)
                needs_import = True

        # 如果内容有变化
        if content != original_content:
            # 检查是否已经有 import
            if "from config.path_config import" not in content and needs_import:
                # 在 import 部分添加
                import_pos = content.find("import ")
                if import_pos != -1:
                    # 找到第一个非 import/from 的行
                    lines = content.split('\n')
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.strip() and not line.strip().startswith('#'):
                            if not (line.startswith('import ') or line.startswith('from ')):
                                insert_pos = i
                                break
                            insert_pos = i + 1

                    lines.insert(insert_pos, REQUIRED_IMPORTS)
                    content = '\n'.join(lines)

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ 已转换: {file_path.relative_to(PROJECT_ROOT)}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ 转换失败 {file_path}: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("开始批量转换绝对路径到相对路径")
    print("="*60)

    # 需要处理的 Python 文件
    py_files = list(PROJECT_ROOT.glob("**/*.py"))

    # 排除一些不需要处理的文件
    exclude_patterns = [
        "__pycache__",
        ".git",
        "venv",
        ".venv",
        "scripts/convert_to_relative_paths.py",  # 排除自己
        "config/path_config.py",  # 排除路径配置文件本身
    ]

    filtered_files = []
    for f in py_files:
        should_exclude = False
        for pattern in exclude_patterns:
            if pattern in str(f):
                should_exclude = True
                break
        if not should_exclude:
            filtered_files.append(f)

    print(f"\n找到 {len(filtered_files)} 个Python文件待处理\n")

    converted_count = 0
    for file_path in filtered_files:
        if convert_file(file_path):
            converted_count += 1

    print(f"\n{'='*60}")
    print(f"转换完成！")
    print(f"总计: {len(filtered_files)} 个文件")
    print(f"已转换: {converted_count} 个文件")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
