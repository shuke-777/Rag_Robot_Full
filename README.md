# RAG Chatbot

基于 LangChain 和智谱 AI 的检索增强生成（RAG）聊天机器人，集成 Rerank 技术，具备完整的评估体系和数据库持久化。

## 核心架构

本项目采用分层架构设计，模块解耦，易于扩展和维护：

```
┌─────────────────────────────────────────────────┐
│          应用层 (Application Layer)              │
│              main.py (RAGApplication)           │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│          服务层 (Service Layer)                  │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │ RAG Pipeline │  │ Rerank Engine│            │
│  │  检索 + 生成  │  │  智能重排序   │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │对话管理模块   │  │ 评估系统      │            │
│  │历史感知/重构  │  │ Metrics计算   │            │
│  └──────────────┘  └──────────────┘            │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│          数据层 (Data Layer)                     │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  FAISS向量库 │  │ SQLite数据库  │            │
│  │  知识检索     │  │  对话历史     │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  ┌──────────────────────────────┐              │
│  │     知识库管理 (KB Manager)    │              │
│  │  文档加载/分块/索引构建         │              │
│  └──────────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

### 设计特点

- **分层解耦**：应用层、服务层、数据层职责清晰，便于独立测试和替换
- **模块化**：RAG Pipeline、Rerank、对话管理、评估系统独立封装
- **可配置**：统一配置管理（`config/rag_config.py`），支持热切换知识库和模型
- **可扩展**：Rerank 采用插件式设计，易于集成其他算法（BGE、Cohere 等）
- **数据持久化**：SQLAlchemy ORM 管理对话历史，支持跨会话查询

## 技术栈

| 模块         | 技术选型                     |
|------------|--------------------------|
| LLM        | 智谱 AI GLM-4.5           |
| Embeddings | 智谱 AI embedding-2 (768维) |
| 向量检索      | FAISS (高效相似度搜索)         |
| 框架         | LangChain                |
| 数据库       | SQLite + SQLAlchemy      |
| Rerank     | BGE Reranker Large (CrossEncoder) |

## 技术亮点

### 1. Rerank 性能优化

在 15 个测试问题上的评估结果对比：

| 指标          | 无 Rerank | 有 Rerank | 提升       |
|-------------|---------|---------|----------|
| Recall@3    | 0.618   | 0.674   | +9.1%    |
| Recall@5    | 0.693   | 0.762   | +10.0%   |
| Precision@3 | 0.533   | 0.600   | +12.6%   |
| MRR         | 0.767   | 0.800   | +4.3%    |
| 平均检索时间      | 1.52s   | 0.105s  | **快14倍** |

**结论**：Rerank 在显著提升检索准确性的同时，大幅降低了检索延迟。

### 2. 完整评估体系

- **Recall@K / Precision@K**：衡量检索质量
- **MRR (Mean Reciprocal Rank)**：衡量正确答案排名
- **检索时间**：性能基准测试
- **对比实验**：Rerank vs No-Rerank、不同 Chunk Size 对比

### 3. 对话历史感知

- 自动重构用户问题，解决代词指代问题
- 基于历史上下文生成精准查询
- 数据库持久化，支持跨会话对话恢复

## 项目结构

```
rag-chatbot/
├── main.py                       # 应用主入口 (RAGApplication)
├── src/                          # 核心模块实现
│   ├── v3_rerank_rag_private.py  # Rerank 模块 (SimpleRerank)
│   └── v2_rag_with_stream_async.py  # RAG Pipeline 实现
├── kb/                           # 知识库管理
│   ├── kb_list/                  # 多知识库存储
│   │   ├── private_kb/           # 私有知识库
│   │   └── ...                   # 其他知识库
│   └── rag_kb_management.py      # 知识库构建工具
├── db/                           # 数据库层
│   ├── Sql_base.py               # ORM 基础类
│   └── conversation_history.db   # SQLite 数据库
├── config/                       # 配置管理
│   ├── rag_config.py             # RAG 配置
│   └── path_config.py            # 路径配置
├── evaluation/                   # 评估模块
│   ├── evl_full_private.py       # 评估脚本
│   ├── test_dataset_annotated.json  # 标注测试集
│   └── results/                  # 评估结果
└── requirements.txt              # 依赖清单
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 填入智谱 AI API Key

# 3. 下载 BGE Reranker 模型
# 将 bge-reranker-large 模型放到 ~/Desktop/model/ 目录下

# 4. 运行 RAG 应用
python main.py

# 5. 运行评估
cd evaluation && python evl_full_private.py
```

## License

MIT License
