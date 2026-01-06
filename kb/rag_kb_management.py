import json
from pathlib import Path
from datetime import datetime
import shutil
from langchain_community.embeddings.zhipuai import ZhipuAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader,PyPDFLoader,Docx2txtLoader,UnstructuredMarkdownLoader
from path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
from langchain_community.vectorstores import FAISS
from typing import Optional,Union
from langchain_core.documents import Document
from rag_config import ZHIPUEmbeddings
load_dotenv()
batch_size = 32
class KnowledgeBaseManager:
    """
    """
    def __init__(self,kb_path_or_name:str):
        self.kb_name = kb_path_or_name
        self.base_path = Path(kb_path_or_name)
        self.base_path.mkdir(exist_ok=True)
    def create_kb(self,kb_name:str,
                  description:str):
        kb_path = self.base_path / kb_name
        if kb_path.exists():
            print(f'{kb_name} already exists')
            #raise ValueError(f'{kb_name} already exists')
        else:
            kb_path.mkdir()
            #这样的话，exist_ok=True，即使没有创建成功，也不会报错,
            #否则在这里就会报error
            (kb_path/'documents').mkdir(exist_ok=True)
            (kb_path/'vector_store').mkdir(exist_ok=True)
        metadata = {
            'name':kb_name,
            'description':description,
            'create_time':datetime.now().isoformat(),
            'update_time':datetime.now().isoformat(),
            'doc_count':0,
            'chunk_count':0
        }
        with open(kb_path/'metadata.json','w',encoding='utf-8') as f:
            json.dump(metadata,f,ensure_ascii=False)
        print(f"'{kb_name}'创建成功")
        return True

    def delete_kb(self,kb_name:str):
        kb_path = self.base_path / kb_name
        if kb_path.exists():
            shutil.rmtree(kb_path)
            print(f"'{kb_name}'删除成功")
            return True
        else:
            print(f"'{kb_name}'不存在")
            return False

    def list_kb(self):
        kb_list = []
        for kb_name in self.base_path.iterdir():
            if kb_name.is_dir():
                metadata_path = kb_name / 'metadata.json'
                if metadata_path.exists():
                    with open(metadata_path,'r',encoding='utf-8') as f:
                        metadata = json.load(f)
                    kb_list.append(metadata)
        return kb_list

    def get_kb_path(self,kb_name:str):
        if not kb_name:
            return None
        kb_path = self.base_path / kb_name
        if kb_path.exists():
            return kb_path
        self.create_kb(kb_name,description='wiki数据')
        return self.base_path / kb_name

    def update_metadata(self,kb_name:str,**kwargs):
        kb_path = self.get_kb_path(kb_name=kb_name)
        if not kb_path:
            print('知识库不存在')
            return False
        metadata_path = kb_path /'metadata.json'
        if not metadata_path.exists():
            print(f"元数据文件不存在")
            return False

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        metadata.update(kwargs)
        metadata['update_time'] = datetime.now().isoformat()

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
class DocumentProcessor:
    def __init__(self):
        self.embed_model =  ZHIPUEmbeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap = 50,
            #按照Len的长度来进行切割，也可以按照字符数来进行切割word_count
            length_function=len
        )
    def load_split_document(self,file_path:str):
        ext = Path(file_path).suffix.lower()
        print(ext)
        loaders ={
            '.txt':TextLoader,
            '.pdf':PyPDFLoader,
            '.docx':Docx2txtLoader,
            '.md':UnstructuredMarkdownLoader
        }
        if ext not in loaders:
            raise ValueError(f'不支持的文件格式{ext}')
        loader = loaders[ext](file_path)
        loader=loader.load()
        #处理documents格式
        split_doc=self.text_splitter.split_documents(loader)
        return split_doc

class KnowledgeService:
    public_name = ['wiki', 'wiki2', 'wiki_latest']
    def __init__(self,kb_manager: KnowledgeBaseManager, document_processor: DocumentProcessor):
        self.kb_manager = kb_manager
        self.document_processor = document_processor

    def add_documents(self,kb_name:str,file_path:Union[list[str],str],description:str):
        kb_path = self.kb_manager.get_kb_path(kb_name=kb_name)
        if not kb_path:
            print(f'{kb_name}不存在')
            self.kb_manager.create_kb(kb_name,description)
            kb_path = self.kb_manager.get_kb_path(kb_name)
        all_chunk = []
        if  isinstance(file_path,str):
            file_path = [file_path]
        for file_i in file_path:
            try:
                chunk =self.document_processor.load_split_document(file_path = file_i)
                all_chunk.extend(chunk)
                shutil.copy(file_i,kb_path/'documents'/Path(file_i).name)
            except Exception as e:
                print(f"❌ 处理文件 {file_i} 失败: {e}")
                continue
        if not all_chunk:
            print(f'没有处理到任何文件')
            return False
        vector_path = kb_path /'vector_store'
        max_length = 1500
        cleaned_chunks = []
        for doc in all_chunk:
            content = doc.page_content.strip()
            if content and len(content) <= max_length:
                # 移除可能导致问题的特殊字符
                content = content.replace('\x00', '').replace('\r', '\n')
                doc.page_content = content
                cleaned_chunks.append(doc)
        all_chunk = cleaned_chunks
        print(f"总共处理了 {len(all_chunk)} 个文档块")
        if (vector_path/'index.faiss').exists():
            print('本地加载faiss')
            vector_store = FAISS.load_local(
                str(vector_path),
                self.document_processor.embed_model,
                allow_dangerous_deserialization=True
            )
            for i in range(0, len(all_chunk), batch_size):
                batch = all_chunk[i:i+batch_size]
                try:
                    vector_store.add_documents(batch)
                    print(f'已处理 {min(i + batch_size, len(all_chunk))}/{len(all_chunk)} 个文档块')
                except Exception as e:
                    print(f'批次 {i}-{i+batch_size} 处理失败: {e}')
                    for j, doc in enumerate(batch):
                        try:
                            vector_store.add_documents([doc])
                            print(f'  - 文档 {i+j} 处理成功')
                        except Exception as doc_error:
                            print(f'  - 文档 {i+j} 跳过: {doc_error}')
                            continue
        else:
            print(f'创建新向量库')
            first_batch = all_chunk[:batch_size]
            try:
                vector_store = FAISS.from_documents(
                    first_batch,
                    self.document_processor.embed_model
                )
                print(f'已处理 {len(first_batch)}/{len(all_chunk)} 个文档块')
            except Exception as e:
                print(f'创建向量库失败: {e}')
                # 尝试逐个添加来创建向量库
                print('尝试逐个处理文档...')
                vector_store = None
                for i, doc in enumerate(first_batch):
                    try:
                        if vector_store is None:
                            vector_store = FAISS.from_documents([doc], self.document_processor.embed_model)
                            print(f'  - 文档 {i} 成功创建向量库')
                        else:
                            vector_store.add_documents([doc])
                            print(f'  - 文档 {i} 处理成功')
                    except Exception as doc_error:
                        print(f'  - 文档 {i} 跳过: {doc_error}')
                        continue
                #这里最后再检测一下vector_store是不是创建成功，属于是最后检测了。
                if vector_store is None:
                    print('无法创建向量库，所有文档都失败了')
                    return False

            if len(all_chunk) > batch_size:
                for i in range(batch_size, len(all_chunk), batch_size):
                    batch = all_chunk[i:i + batch_size]
                    try:
                        vector_store.add_documents(batch)
                        print(f'已处理 {min(i + batch_size, len(all_chunk))}/{len(all_chunk)} 个文档块')
                    except Exception as e:
                        print(f'批次 {i}-{i+batch_size} 处理失败: {e}')
                        # 尝试逐个添加来找出有问题的文档
                        for j, doc in enumerate(batch):
                            try:
                                vector_store.add_documents([doc])
                                print(f'  - 文档 {i+j} 处理成功')
                            except Exception as doc_error:
                                print(f'  - 文档 {i+j} 跳过: {doc_error}')
                                continue
        # save_vectorstore
        #因为这里的vector_path还是path，但是在langchain中期待传入的还是str的
        vector_store.save_local(str(vector_path))
        #更新metadata
        metadata_path = kb_path / 'metadata.json'
        with open(metadata_path,'r',encoding='utf-8') as f:
            metadata = json.load(f)
        metadata['doc_count'] += len(file_path)
        metadata['chunk_count'] = metadata.get('chunk_count',0)+len(all_chunk)
        metadata['update_time'] = datetime.now().isoformat()
        with open(metadata_path,'w',encoding='utf-8') as f:
            json.dump(metadata,f,ensure_ascii=False,indent=2)
        print(f'成功添加{len(file_path)}个文档，共有{len(all_chunk)}个文档块')
        return True

    def search_kb(self,kb_name:str):
        kb_path = self.kb_manager.get_kb_path(kb_name = kb_name)
        if not kb_path:
            print(f'{kb_name}不存在')
            return None
        vector_path = kb_path / 'vector_store'
        if not (vector_path / 'index.faiss').exists():
            print(f'知识库{kb_name}没有添加文档')
            return []
        vector_store = FAISS.load_local(
            str(vector_path),
            self.document_processor.embed_model,
            allow_dangerous_deserialization=True
        )
        return vector_store

    def add_chunk2vector(self,kb_name:str,file_path:str,description:str):
        kb_path = self.kb_manager.get_kb_path(kb_name = kb_name)

        if kb_name not in self.public_name:
            kb_type = 'private'
        else:
            kb_type = 'public'
        with open(file_path,'r',encoding='utf-8') as f:
            all_chunk = [json.loads(line) for line in f]
        docs = [
            Document(
                page_content=chunk['contents'],
                metadata = {'id':chunk['id'],'title':chunk['title'],'kb_type':kb_type}
        ) for chunk in all_chunk]

        print(f'共读取 {len(docs)} 个文档块')

        vector_store_path = kb_path / 'vector_store' / 'index.faiss'
        batch_size = 32
        shutil.copy(file_path,kb_path/'documents'/Path(file_path).name)
        # 判断向量库是否存在
        if vector_store_path.exists():
            # 加载已有向量库
            print(f'本地知识库{kb_name}已经存在，loading中')
            vector_store = FAISS.load_local(
                str(kb_path/'vector_store'),
                embeddings=self.document_processor.embed_model,
                allow_dangerous_deserialization=True
            )

            # 批量添加文档
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                vector_store.add_documents(batch)
                print(f'已处理 {min(i + batch_size, len(docs))}/{len(docs)} 个文档块')

            # 保存向量库
            vector_store.save_local(folder_path=str(kb_path/'vector_store'))
            print(f'成功添加 {len(docs)} 个文档块')

        else:
            # 创建新向量库
            print(f'创建新向量库 {kb_name}')
            if not kb_path.exists():
                self.kb_manager.create_kb(kb_name=kb_name, description=description)
                kb_path = self.kb_manager.get_kb_path(kb_name)

            # 先创建初始向量库
            first_batch = docs[:batch_size]
            vector_store = FAISS.from_documents(
                documents=first_batch,
                embedding=self.document_processor.embed_model
            )
            print(f'已处理 {len(first_batch)}/{len(docs)} 个文档块')
            if len(docs) > batch_size:
                for i in range(batch_size, len(docs), batch_size):
                    batch = docs[i:i + batch_size]
                    vector_store.add_documents(batch)
                    print(f'已处理 {min(i + batch_size, len(docs))}/{len(docs)} 个文档块')

            vector_store.save_local(folder_path=str(kb_path / 'vector_store'))
            print(f'{kb_name}知识库创建成功')

        with open(kb_path/'metadata.json','r',encoding='utf-8') as f:
            metadata = json.load(f)
        metadata['doc_count'] += 1
        metadata['chunk_count'] = metadata.get('chunk_count', 0) + len(docs)
        metadata['update_time'] = datetime.now().isoformat()
        with open(kb_path/'metadata.json','w',encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return True

if __name__ == '__main__':
    kb_path_or_name = str(KB_LIST_DIR)
    #doc1 = '/Users/salutethedawn/Desktop/编程用文件夹/西瓜/hw项目跟敲/private项目/解析木--实验计划.docx'
    KS = KnowledgeService(
        KnowledgeBaseManager(kb_path_or_name=kb_path_or_name),document_processor = DocumentProcessor())
    # #KS.add_documents('树木论文',doc2,description='关于技术文档的rag')
    # #print(KS.kb_manager.list_kb())
    # vec_result= KS.search_kb('树木论文')
    # retriver = vec_result.as_retriever(search_kwargs = {'k':3})
    # result=retriver.invoke('医学类型有哪些')
    # for i in result:
    #     print(i.page_content,'\n\n')
    #KS.kb_manager.delete_kb('wiki')
    KS.add_chunk2vector(kb_name='Controlled_chunk_250',
                        file_path=str(KB_SAVE_PATH_DIR / 'python_chunk_250.jsonl'),
                        description='chunk_250')
