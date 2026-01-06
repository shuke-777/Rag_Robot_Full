import json

from rag_kb_management import  DocumentProcessor
from pathlib import Path
from unstructured.partition.pdf import partition_pdf

from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
def parse_pdf_with_unstructured(pdf_path,output_dir = None):
    pdf_name = Path(pdf_path)
    print(f'pdf_name:{pdf_name}')
    if output_dir is None:
        output_dir = pdf_name.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    print(output_dir)
    elements = partition_pdf(
        filename=str(pdf_path),
        strategy='hi_res',
        infer_table_structure = True,
        model_name = 'yolox',
        languages=['chi_sim', 'eng']
    )
    print(f'解析完成，一共{len(elements)}个元素')
    element_file = output_dir / f'{pdf_name.stem}_parse.json'

    with open(element_file, 'w+', encoding='utf-8') as f:
        ele_data = []
        for i,e in enumerate(elements):
            ele_data.append(
                {
                    'id':i,
                    'type': str(e.category)if hasattr(e,'category') else e.__class__.__name__,
                    'text':str(e),
                    'metadata': e.metadata.to_dict() if hasattr(e.metadata,'to_dict') else {}
                }
            )
        # 【修改1】将 json.dump 移到 with 块内部（增加了4个空格的缩进），这样文件 f 还是打开状态才能写入
        json.dump(ele_data,f,ensure_ascii=False,indent=4)
    print(f'已经保存到: {element_file}')

    include_types = {
          'Title', 'NarrativeText', 'ListItem',
          'Table', 'Formula', 'FigureCaption',
          'UncategorizedText'
      }
    filtered_texts = []
    current_section = ""
    #{'Title', 'Formula', 'FigureCaption', 'Table', 'Image', 'ListItem', 'UncategorizedText', 'NarrativeText', 'Header'}
    for e in elements:
        category = str(e.category) if hasattr(e, 'category') else e.__class__.__name__

        if category not in include_types:
            continue
    # 基本信息
        chunk = {
            'text': str(e),
            'type': category,
            'page': e.metadata.page_number if hasattr(e.metadata,
                                                      'page_number') else None,
        }
        # 特殊处理
        if category == 'Title':
            current_section = str(e)
            chunk['is_section_title'] = True

        elif category == 'Table':
            # 表格特殊标记
            chunk['text'] = f"[表格]\n{chunk['text']}"
            if hasattr(e.metadata, 'text_as_html'):
                chunk['table_html'] = e.metadata.text_as_html

        elif category == 'Formula':
            chunk['text'] = f"[公式] {chunk['text']}"

        elif category == 'FigureCaption':
            chunk['text'] = f"[图表说明] {chunk['text']}"

        # 给每个chunk添加章节上下文
        chunk['section'] = current_section

        filtered_texts.append(chunk)

    extact_path = output_dir / f'{pdf_name.stem}_extact.json'
    with open(extact_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_texts, f, ensure_ascii=False, indent=4)
    print(f'已经保存到: {extact_path}')
    return filtered_texts

if __name__ == '__main__':
    file = str(RAW_DATA_DIR / '复杂场景下的改进YOLOv8n安全帽佩戴检测算法_雷源毅.pdf')
    output_dir = str(KB_PARSE_RESULT_DIR)
    #parse_pdf_with_unstructured(pdf_path=file,output_dir=output_dir)
    # document_processor = DocumentProcessor()
    # print(document_processor.text_splitter)
    # result = document_processor.load_split_document(file_path=file)
    import json
    file_exact = str(KB_PARSE_RESULT_DIR / '复杂场景下的改进YOLOv8n安全帽佩戴检测算法_雷源毅_extact.json')
    file_source = str(KB_PARSE_RESULT_DIR / '复杂场景下的改进YOLOv8n安全帽佩戴检测算法_雷源毅_parse.json')
    r1=json.load(open(file_exact,'r',encoding='utf-8'))
    r2 = json.load(open(file_source,'r',encoding='utf-8'))
    print('exact_len',len(r1))
    print('source_len',len(r2))