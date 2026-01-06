from langchain_community.document_loaders import Docx2txtLoader
from config.path_config import DOCUMENTS_DIR

Doc=Docx2txtLoader(str(DOCUMENTS_DIR / '20_前端性能优化.docx'))
result = Doc.load()
for i in result:
    print(i.page_content)
    print(i.metadata)