

from pathlib import Path
import os

# 项目根目录（基于本文件位置自动计算）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw_data"
DOCUMENTS_DIR = RAW_DATA_DIR / "documents"
OCR_RESULTS_DIR = DATA_DIR / "ocr_results"

# 知识库目录
KB_DIR = PROJECT_ROOT / "kb"
KB_LIST_DIR = KB_DIR / "kb_list"
KB_SAVE_PATH_DIR = KB_DIR / "save_path"
KB_PARSE_RESULT_DIR = KB_DIR / "parse_result"

# 知识库具体路径
PRIVATE_KB_DIR = KB_LIST_DIR / "private_kb"
PRIVATE_KB_SOURCE = PRIVATE_KB_DIR / "source"
PRIVATE_KB_VECTOR = PRIVATE_KB_DIR / "vector_store"
PRIVATE_KB_DOCUMENTS = PRIVATE_KB_DIR / "documents"

TECH_DOCS_KB_DIR = KB_LIST_DIR / "技术文档"
WIKI_KB_DIR = KB_LIST_DIR / "wiki"
CONTROLLED_CHUNK_KB_DIR = KB_LIST_DIR / "Controlled_chunk_250"
RAG_TEST_KB_DIR = KB_LIST_DIR / "rag_test_kb"

# 评估目录
EVALUATION_DIR = PROJECT_ROOT / "evaluation"
EVALUATION_RESULTS_DIR = EVALUATION_DIR / "results"
TEST_DATASET_PATH = EVALUATION_DIR / "test_dataset.json"
TEST_DATASET_ANNOTATED_PATH = EVALUATION_DIR / "test_dataset_annotated.json"

# 源代码目录
SRC_DIR = PROJECT_ROOT / "src"

# 数据库目录
DB_DIR = PROJECT_ROOT / "db"
DB_FILE = DB_DIR / "conversation_history.db"

# 向量存储目录
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

# 配置目录
CONFIG_DIR = PROJECT_ROOT / "config"

# 服务器目录
SERVER_DIR = PROJECT_ROOT / "server"

# 外部模型路径（可以通过环境变量覆盖）
# 这个路径指向外部下载的模型，不在项目内
EXTERNAL_MODEL_DIR = os.getenv(
    "EXTERNAL_MODEL_DIR",
    str(Path.home() / "Desktop" / "model")  # 默认值
)
BGE_RERANKER_MODEL = os.getenv(
    "BGE_RERANKER_MODEL",
    str(Path(EXTERNAL_MODEL_DIR) / "bge-reranker-large")
)


def get_kb_path(kb_name: str) -> Path:
    """
    获取指定知识库的路径

    Args:
        kb_name: 知识库名称

    Returns:
        知识库路径 Path 对象
    """
    return KB_LIST_DIR / kb_name


def get_kb_vector_store(kb_name: str) -> Path:
    """获取知识库的向量存储路径"""
    return get_kb_path(kb_name) / "vector_store"


def get_kb_source(kb_name: str) -> Path:
    """获取知识库的源文件路径"""
    return get_kb_path(kb_name) / "source"


def get_kb_documents(kb_name: str) -> Path:
    """获取知识库的文档路径"""
    return get_kb_path(kb_name) / "documents"


def ensure_dir(path: Path) -> Path:
    """
    确保目录存在，不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path 对象
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


# 确保关键目录存在
def init_directories():
    """初始化所有必要的目录"""
    dirs = [
        DATA_DIR,
        RAW_DATA_DIR,
        DOCUMENTS_DIR,
        OCR_RESULTS_DIR,
        KB_DIR,
        KB_LIST_DIR,
        KB_SAVE_PATH_DIR,
        KB_PARSE_RESULT_DIR,
        EVALUATION_DIR,
        EVALUATION_RESULTS_DIR,
        DB_DIR,
        VECTOR_STORE_DIR,
    ]

    for dir_path in dirs:
        ensure_dir(dir_path)

    print(f"✅ 项目目录初始化完成，根目录: {PROJECT_ROOT}")


# 添加项目根目录到 Python 路径（用于替代 sys.path.append）
import sys
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


if __name__ == "__main__":
    # 测试路径配置
    print("="*60)
    print("项目路径配置")
    print("="*60)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"数据目录: {DATA_DIR}")
    print(f"知识库目录: {KB_LIST_DIR}")
    print(f"评估目录: {EVALUATION_DIR}")
    print(f"Private KB 向量存储: {PRIVATE_KB_VECTOR}")
    print(f"BGE Reranker 模型: {BGE_RERANKER_MODEL}")
    print("="*60)

    # 初始化目录
    init_directories()
