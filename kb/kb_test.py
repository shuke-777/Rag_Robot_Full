from langchain_community.vectorstores import FAISS
from rag_config import ZHIPUEmbeddings
from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
embed = ZHIPUEmbeddings
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
path = str(PRIVATE_KB_VECTOR)
kb = FAISS.load_local(path, embed,allow_dangerous_deserialization=True)
retriever = kb.as_retriever(search_kwargs={'k':3})
result_page_content=[doc.page_content for doc in retriever.invoke('ACM电脑分类有哪些的')]
for i ,doc in enumerate(retriever.invoke('ACM电脑分类有哪些')):
    print(f"=== 结果 {i} ===")
    print(f"private/public:{doc.metadata.get('kb_type')}")
    print(f"🗄️  知识库: {doc.metadata.get('kb_source','unknow')}")
    print(f"📄 文档: {doc.metadata.get('title', 'Unknown')}")
    print(f"📝 内容: {doc.page_content[:150]}...\n")
