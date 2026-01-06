from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
"""
私有知识库解析器 - 方案2：JSONL 保存完整 metadata

功能：
1. 解析 Markdown 文件，提取标题和章节
2. 生成 Document 对象
3. 保存为 JSONL 格式（包含完整 metadata）
4. 兼容 add_chunk2vector 方法
"""
import warnings

warnings.filterwarnings('ignore', category=UserWarning,
                        module='pkg_resources')
from langchain_community.document_loaders import UnstructuredMarkdownLoader, Docx2txtLoader
import re
import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Tuple, Dict

def _extract_sections(file_path: Path) -> Tuple[List[Dict], str]:

    if not file_path.is_file():
        raise ValueError(f"路径必须是文件: {file_path}")

    if file_path.suffix != '.md':
        raise ValueError(f"只支持 .md 文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = []
    lines = content.split('\n')
    current_title = None
    current_content = []
    doc_title = None

    for line in lines:
        # 检测主标题（一级标题：# 标题）
        main_match = re.match(r'^#\s+(.+)$', line)
        if main_match and doc_title is None:
            doc_title = main_match.group(1).strip()
            continue

        # 检测章节标题（二级标题：## 标题）
        section_match = re.match(r'^##\s+(.+)$', line)
        if section_match:
            if current_title:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    sections.append({
                        'title': current_title,
                        'content': content_text
                    })
            current_title = section_match.group(1).strip()
            current_content = []
        else:
            if current_title:
                current_content.append(line)

    if current_title:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            sections.append({
                'title': current_title,
                'content': content_text
            })

    # 如果没有找到主标题，使用文件名
    if doc_title is None:
        doc_title = file_path.stem

    return sections, doc_title

def _extract_word_sections(file_path: Path) -> Tuple[List[Dict], str]:
    file_path = Path(file_path)
    if file_path.suffix not in ['.docx', '.doc']:
        raise ValueError(f"只支持 .docx 或 .doc 文件: {file_path}")

    loader = Docx2txtLoader(file_path)
    docs = loader.load()

    if not docs:
        return [], file_path.stem

    content = docs[0].page_content

    lines = content.split('\n')

    sections = []
    doc_title = None
    current_title = None
    current_content = []

    for line in lines:
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        if doc_title is None:
            if not re.match(r'^\d+[.、]', line) and not re.match(r'^[#]+\s+', line):
                doc_title = line
                continue
            else:
                doc_title = file_path.stem

        # 检测章节标题
        is_section_title = False

        # 模式1: "1. xxx", "2. xxx" 等（单层编号）
        if re.match(r'^\d+\.\s+', line):
            is_section_title = True
        # 模式2: "1.1 xxx", "2.3 xxx" 等（两层编号）
        elif re.match(r'^\d+\.\d+\s+', line):
            is_section_title = True
        # 模式3: "## " 开头
        elif re.match(r'^##\s+', line):
            is_section_title = True
        # 模式4: "（一）", "（二）" 等
        elif re.match(r'^[（(][一二三四五六七八九十]+[）)]\s*', line):
            is_section_title = True
        # 模式5: "一、", "二、" 等
        elif re.match(r'^[一二三四五六七八九十]+[、]\s*', line):
            is_section_title = True

        if is_section_title:
            # 保存上一个章节
            if current_title:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    sections.append({
                        'title': current_title,
                        'content': content_text
                    })

            current_title = re.sub(r'^[\d#（(一二三四五六七八九十]+[.、\s）)]+', '', line).strip()
            if not current_title:
                current_title = line
            current_content = []
        else:

            if current_title:
                current_content.append(line)

    # 保存最后一个章节
    if current_title:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            sections.append({
                'title': current_title,
                'content': content_text
            })

    if doc_title is None:
        doc_title = file_path.stem

    return sections, doc_title



def parse(folder_path: str, kb_type: str = 'private', category: str = None,
          chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:

    folder_path = Path(folder_path)

    # 检查路径是否存在
    if not folder_path.exists():
        print('路径不存在')
    # else:
    #     folder_path.mkdir(parents=True, exist_ok=True)

    # 获取所有 .md 和 .docx 文件
    all_files = []
    if folder_path.is_dir():
        md_files = list(folder_path.glob('*.md'))
        docx_files = list(folder_path.glob('*.docx'))
        all_files = md_files + docx_files

        if not all_files:
            print(f'⚠️ 文件夹中没有找到 .md 或 .docx 文件: {folder_path}')
            return []
        print(f'📁 在文件夹中找到 {len(md_files)} 个 .md 文件, {len(docx_files)} 个 .docx 文件')
    elif folder_path.is_file() and folder_path.suffix in ['.md', '.docx']:

        all_files = [folder_path]
        print(f'📄 检测到单个 {folder_path.suffix} 文件')
    else:
        print(f'⚠️ 不是文件夹或支持的文件类型: {folder_path}')
        return []

    # 创建文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    # 处理所有文件
    all_docs = []

    for file in all_files:
        print(f'\n📖 开始解析文件: {file.name}')

        try:
            # 根据文件类型选择解析函数
            if file.suffix == '.md':
                sections, doc_title = _extract_sections(file)
            elif file.suffix == '.docx':
                sections, doc_title = _extract_word_sections(file)
            else:
                print(f'⚠️ 不支持的文件类型: {file.suffix}')
                continue

            if not sections:
                print(f'⚠️ 文件 {file.name} 未提取到任何章节，跳过')
                continue

            print(f'📚 文档标题: {doc_title}')
            print(f'📑 提取到 {len(sections)} 个章节')

            # 2. 获取文件名和分类
            file_name = file.stem
            current_category = category if category else doc_title

            # 3. 处理每个章节
            for section_idx, section in enumerate(sections):
                # 创建初始 Document
                doc = Document(
                    page_content=section['content'],
                    metadata={
                        'doc_title': doc_title,
                        'section_title': section['title'],
                        'source': str(file),
                        'file_name': file_name,
                        'kb_type': kb_type,
                        'category': current_category,
                        'section_index': section_idx
                    }
                )

                # 如果章节太长，进一步切分
                if len(section['content']) > chunk_size:
                    print(f"  ✂️  章节 '{section['title']}' 较长 ({len(section['content'])} 字符)，切分中...")
                    chunks = text_splitter.split_documents([doc])
                else:
                    chunks = [doc]

                # 为每个 chunk 添加详细的 metadata
                for chunk_idx, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        'id': f"{file_name}_s{section_idx}_c{chunk_idx}",
                        'title': section['title'],  # 章节标题作为 title
                        'chunk_index_in_section': chunk_idx,
                        'total_chunks_in_section': len(chunks)
                    })
                    all_docs.append(chunk)

            print(f'✅ {file.name} 解析完成')

        except Exception as e:
            print(f'❌ 处理文件 {file.name} 失败: {e}')
            continue

    for global_idx, doc in enumerate(all_docs):
        doc.metadata['global_chunk_index'] = global_idx
        doc.metadata['total_chunks'] = len(all_docs)

    print(f'\n✅ 总计解析完成，共生成 {len(all_docs)} 个文档块\n')

    return all_docs


def save_to_jsonl_with_full_metadata(docs: List[Document], output_path: str):

    with open(output_path, 'w', encoding='utf-8') as f:
        for doc in docs:
            item = {
                'id': doc.metadata['id'],
                'title': doc.metadata['title'],
                'contents': doc.page_content,
                'metadata': {
                    'doc_title': doc.metadata.get('doc_title'),
                    'section_title': doc.metadata.get('section_title'),
                    'source': doc.metadata.get('source'),
                    'file_name': doc.metadata.get('file_name'),
                    'kb_type': doc.metadata.get('kb_type'),
                    'category': doc.metadata.get('category'),
                    'section_index': doc.metadata.get('section_index'),
                    'chunk_index_in_section': doc.metadata.get('chunk_index_in_section'),
                    'total_chunks_in_section': doc.metadata.get('total_chunks_in_section'),
                    'global_chunk_index': doc.metadata.get('global_chunk_index'),
                    'total_chunks': doc.metadata.get('total_chunks')
                }
            }
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f'💾 已保存 {len(docs)} 个文档块（含完整metadata）到: {output_path}')



if __name__ == '__main__':
    folder_path = str(DOCUMENTS_DIR)

    # 解析文档
    # docs = parse(
    #     folder_path,
    #     kb_type='private',
    #     category='python_tutorial',
    #     chunk_size=500,
    #     chunk_overlap=50
    # )

    output_path = str(KB_SAVE_PATH_DIR / 'python_chunk_250.jsonl')
    #save_to_jsonl_with_full_metadata(docs, output_path)
    # def parse(folder_path: str, kb_type: str = 'private', category: str = None,
    #           chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    folder_path = str(DOCUMENTS_DIR)
    docs = parse(folder_path=folder_path,kb_type='private',chunk_size=250,chunk_overlap=50)
    save_to_jsonl_with_full_metadata(docs, output_path)