# LangChain 快速入门指南

## 1. LangChain 简介

LangChain 是一个用于开发由大语言模型（LLM）驱动的应用程序的框架。它简化了 LLM 应用程序生命周期的每个阶段：

- **开发**: 使用 LangChain 的开源组件和第三方集成构建应用程序
- **生产化**: 使用 LangSmith 检查、监控和评估您的链
- **部署**: 使用 LangServe 将任何链转换为 API

### 1.1 核心概念

- **Models**: 与各种 LLM 提供商的接口
- **Prompts**: 管理和优化提示词
- **Chains**: 将多个组件串联起来
- **Agents**: 让 LLM 决定采取哪些行动
- **Memory**: 在链的多次调用之间持久化状态
- **Indexes**: 结构化数据以便 LLM 可以与之交互

## 2. 安装和配置

### 2.1 安装 LangChain

```bash
# 安装核心包
pip install langchain

# 安装常用集成
pip install langchain-community
pip install langchain-openai

# 安装可选依赖
pip install faiss-cpu  # 向量存储
pip install chromadb   # 另一个向量存储选项
```

### 2.2 配置 API 密钥

```python
import os

# 方式1: 直接设置环境变量
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 方式2: 使用 .env 文件
from dotenv import load_dotenv
load_dotenv()  # 从 .env 文件加载环境变量
```

## 3. 基础使用

### 3.1 调用 LLM

```python
from langchain_openai import ChatOpenAI

# 初始化模型
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000
)

# 调用模型
response = llm.invoke("你好，请介绍一下自己")
print(response.content)
```

### 3.2 使用提示词模板

```python
from langchain.prompts import ChatPromptTemplate

# 创建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的AI助手。"),
    ("human", "请用{language}回答：{question}")
])

# 格式化提示词
messages = prompt.format_messages(
    language="中文",
    question="什么是机器学习？"
)

# 调用模型
response = llm.invoke(messages)
print(response.content)
```

### 3.3 创建简单链

```python
from langchain.chains import LLMChain

# 创建链
chain = prompt | llm

# 调用链
result = chain.invoke({
    "language": "中文",
    "question": "什么是深度学习？"
})

print(result.content)
```

## 4. 检索增强生成 (RAG)

### 4.1 加载文档

```python
from langchain_community.document_loaders import TextLoader

# 加载文本文件
loader = TextLoader("document.txt", encoding="utf-8")
documents = loader.load()

# 加载多个文档
from langchain_community.document_loaders import DirectoryLoader

loader = DirectoryLoader("./documents", glob="**/*.txt")
documents = loader.load()
```

### 4.2 文本分割

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)

# 分割文档
splits = text_splitter.split_documents(documents)
print(f"分割成 {len(splits)} 个chunks")
```

### 4.3 创建向量存储

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 加载 embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-zh-v1.5"
)

# 创建向量存储
vectorstore = FAISS.from_documents(
    documents=splits,
    embedding=embeddings
)

# 保存向量存储
vectorstore.save_local("vectorstore")

# 加载向量存储
loaded_vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)
```

### 4.4 构建 RAG 链

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 创建提示词模板
template = """使用以下上下文来回答问题。如果你不知道答案，就说你不知道，不要编造答案。

上下文：
{context}

问题：{question}

答案："""

QA_PROMPT = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# 创建 RAG 链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": QA_PROMPT},
    return_source_documents=True
)

# 使用 RAG 链
result = qa_chain.invoke({"query": "什么是 RAG？"})
print("答案:", result["result"])
print("\n来源文档:")
for doc in result["source_documents"]:
    print(f"- {doc.page_content[:100]}...")
```

## 5. 对话记忆

### 5.1 使用 ConversationBufferMemory

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 创建记忆
memory = ConversationBufferMemory()

# 创建对话链
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 进行对话
response1 = conversation.predict(input="你好，我叫张三")
print(response1)

response2 = conversation.predict(input="你还记得我的名字吗？")
print(response2)  # 应该能记住名字是"张三"
```

### 5.2 使用 ConversationSummaryMemory

```python
from langchain.memory import ConversationSummaryMemory

# 创建总结式记忆（节省token）
memory = ConversationSummaryMemory(llm=llm)

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# 进行多轮对话
conversation.predict(input="我正在学习 LangChain")
conversation.predict(input="它的主要功能是什么？")
conversation.predict(input="你刚才说了什么？")
```

## 6. Agents（代理）

### 6.1 创建工具

```python
from langchain.agents import Tool
from langchain.tools import BaseTool
from typing import Optional

# 方式1: 使用函数创建工具
def get_current_time(query: str) -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

time_tool = Tool(
    name="CurrentTime",
    func=get_current_time,
    description="用于获取当前时间。输入应该是一个查询。"
)

# 方式2: 继承 BaseTool 创建工具
class CalculatorTool(BaseTool):
    name = "Calculator"
    description = "用于进行数学计算。输入应该是一个数学表达式。"

    def _run(self, query: str) -> str:
        """执行计算"""
        try:
            return str(eval(query))
        except Exception as e:
            return f"计算错误: {str(e)}"

    async def _arun(self, query: str) -> str:
        """异步执行"""
        return self._run(query)

calculator = CalculatorTool()
```

### 6.2 创建 Agent

```python
from langchain.agents import initialize_agent, AgentType

# 定义工具列表
tools = [time_tool, calculator]

# 初始化 agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 使用 agent
response = agent.run("现在几点了？")
print(response)

response = agent.run("计算 15 * 23")
print(response)
```

## 7. 输出解析器

### 7.1 结构化输出

```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# 定义输出模型
class Person(BaseModel):
    name: str = Field(description="人的名字")
    age: int = Field(description="人的年龄")
    occupation: str = Field(description="人的职业")

# 创建解析器
parser = PydanticOutputParser(pydantic_object=Person)

# 创建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "从用户输入中提取人物信息。\n{format_instructions}"),
    ("human", "{input}")
])

# 构建链
chain = prompt | llm | parser

# 使用
result = chain.invoke({
    "input": "张三今年30岁，是一名软件工程师",
    "format_instructions": parser.get_format_instructions()
})

print(result)  # Person(name='张三', age=30, occupation='软件工程师')
```

## 8. 流式输出

### 8.1 同步流式输出

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 创建支持流式输出的 LLM
streaming_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# 流式输出
streaming_llm.invoke("写一首关于春天的诗")
```

### 8.2 异步流式输出

```python
import asyncio

async def stream_response():
    async for chunk in streaming_llm.astream("讲一个笑话"):
        print(chunk.content, end="", flush=True)

# 运行异步函数
asyncio.run(stream_response())
```

## 9. 完整 RAG 应用示例

```python
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGApplication:
    def __init__(self, doc_dir, model_name="gpt-3.5-turbo"):
        # 初始化 LLM
        self.llm = ChatOpenAI(model=model_name, temperature=0)

        # 初始化 embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-base-zh-v1.5"
        )

        # 加载和处理文档
        self.vectorstore = self._load_documents(doc_dir)

        # 创建 QA 链
        self.qa_chain = self._create_qa_chain()

    def _load_documents(self, doc_dir):
        """加载和向量化文档"""
        # 加载文档
        loader = DirectoryLoader(doc_dir, glob="**/*.txt")
        documents = loader.load()

        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)

        # 创建向量存储
        vectorstore = FAISS.from_documents(splits, self.embeddings)
        return vectorstore

    def _create_qa_chain(self):
        """创建问答链"""
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )

        template = """基于以下上下文回答问题。如果不知道答案，就说不知道。

        上下文：
        {context}

        问题：{question}

        答案："""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        return qa_chain

    def ask(self, question):
        """提问"""
        result = self.qa_chain.invoke({"query": question})
        return {
            "answer": result["result"],
            "sources": [doc.page_content for doc in result["source_documents"]]
        }

# 使用
app = RAGApplication("./documents")
result = app.ask("什么是 LangChain？")
print("答案:", result["answer"])
```

## 10. 最佳实践

### 10.1 错误处理

```python
from langchain.callbacks import get_openai_callback

try:
    with get_openai_callback() as cb:
        result = qa_chain.invoke({"query": "你的问题"})
        print(f"Tokens used: {cb.total_tokens}")
        print(f"Cost: ${cb.total_cost:.4f}")
except Exception as e:
    print(f"Error: {e}")
```

### 10.2 缓存

```python
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

# 启用缓存
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# 后续相同的查询会从缓存返回，节省 API 调用
```

### 10.3 调试

```python
from langchain.globals import set_debug

# 启用调试模式
set_debug(True)

# 会打印详细的执行信息
result = qa_chain.invoke({"query": "你的问题"})
```

## 总结

LangChain 提供了强大的工具链来构建 LLM 应用：

1. **Models**: 统一的 LLM 接口
2. **Prompts**: 提示词管理
3. **Chains**: 组件串联
4. **Memory**: 对话记忆
5. **Agents**: 智能代理
6. **RAG**: 检索增强生成

掌握这些核心概念，你就可以快速构建强大的 LLM 应用程序了！
