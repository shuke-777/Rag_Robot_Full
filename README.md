# RAG Chatbot

基于 LangChain 和智谱AI的检索增强生成(RAG)聊天机器人，支持对话历史管理。


## 功能特点

- 基于 FAISS 的向量存储和检索
- 智谱AI Embedding 和 GLM-4.5 大模型
- 支持对话历史感知的问答
- 手动和自动两种历史管理方式
- Word 文档加载和智能分割

## 技术栈

- **LangChain**: RAG 框架
- **FAISS**: 向量数据库
- **智谱AI**: LLM 和 Embedding 服务
- **Python-docx**: 文档处理

## 项目结构

```
rag-chatbot/
├── src/
│   └── rag_with_history.py    # 主程序
├── data/                       # 数据文件目录
├── vector_store/               # 向量存储（自动生成）
├── .env.example               # 环境变量模板
├── .gitignore
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
ZHIPU_MODEL_NAME=glm-4.5
ZHIPUAI_API_KEY=your_actual_api_key_here
ZHIPUAI_URL=https://open.bigmodel.cn/api/paas/v4
```

### 3. 准备数据

将你的 Word 文档放入 `data/` 目录。

### 4. 运行程序

```bash
cd src
python rag_with_history.py
```

## 使用说明

### 首次运行

首次运行时需要创建向量存储：

1. 在 `src/rag_with_history.py` 中取消注释第144行：
   ```python
   create_vector_store(t1_split_text, "1201Faiss.faiss")
   ```

2. 运行程序生成向量索引

3. 之后注释掉该行，直接加载已有索引

### 两种历史管理方式

**方式1：手动管理聊天历史**
```python
chat_history = []
result = qa_chain.invoke({'input': question, 'chat_history': chat_history})
chat_history.extend([HumanMessage(content=question), AIMessage(content=result)])
```

**方式2：自动管理聊天历史**
```python
rag_chain = get_rag_chain(qa_chain)
rag_chain.invoke(
    {'input': question},
    config={'configurable': {'session_id': 'user_1'}}
)
```

## 核心功能

### 文档加载与分割
- 支持 Word 文档 (.docx)
- 自动分段和智能分块
- chunk_size=200, chunk_overlap=20

### 向量检索
- FAISS 向量存储
- 智谱AI embedding-2 模型
- Top-K 检索 (默认 k=3)

### 对话历史感知
- 自动重构用户问题
- 结合上下文理解代词指向
- 提升多轮对话体验

## 开发计划

- [ ] 支持更多文档格式 (PDF, TXT, Markdown)
- [ ] Web UI 界面
- [ ] 多用户会话管理
- [ ] 检索结果评分可视化

## 致谢
- 感谢我的女朋友@luojia和我们的家人@black
- 他们在我每次焦头烂额的时候听我一直说话和陪我玩耍

## 许可证

MIT License
