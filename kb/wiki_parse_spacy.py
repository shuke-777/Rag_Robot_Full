import re

import spacy
import wikipediaapi
from pathlib import Path
from tqdm import tqdm
from typing import Tuple, List, Dict
import json
from config.path_config import (
    PROJECT_ROOT, KB_LIST_DIR, KB_DIR, KB_SAVE_PATH_DIR, KB_PARSE_RESULT_DIR,
    PRIVATE_KB_DIR, PRIVATE_KB_VECTOR, DATA_DIR, RAW_DATA_DIR, DOCUMENTS_DIR,
    EVALUATION_DIR, EVALUATION_RESULTS_DIR, TEST_DATASET_PATH,
    VECTOR_STORE_DIR, DB_DIR, BGE_RERANKER_MODEL
)
save_path_src = Path(str(KB_DIR))
save_path = save_path_src/'save_path'
model_name = 'zh_core_web_sm'
class WikipediaFetcher:
    """Wikipedia文章获取器"""

    def __init__(self, language='zh', user_agent='RAG-ChatBot/1.0',chunk_size = 300):
        """
        初始化Wikipedia API

        Args:
            language: 语言代码（zh=中文，en=英文）
            user_agent: 用户代理字符串
        """
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent=user_agent
        )
        self.nlp = spacy.load(model_name)
        # 定义技术相关的主题列表
        self.tech_topics = [
            # AI & 机器学习
            '人工智能', '机器学习', '深度学习', '神经网络', '卷积神经网络',
            '循环神经网络', '自然语言处理', '计算机视觉', '强化学习',

            # 编程语言
            'Python', 'Java', 'JavaScript', 'C++', 'Go语言',

            # 数据结构与算法
            '数据结构', '算法', '排序算法', '搜索算法', '哈希表',
            '二叉树', '图论', '动态规划',

            # Web开发
            'HTTP', 'RESTful', 'API', 'Web开发', '前端', '后端',
            'React', 'Vue.js', 'Django', 'Flask',

            # 数据库
            '数据库', 'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',

            # 云计算与DevOps
            '云计算', 'Docker', 'Kubernetes', 'DevOps', '微服务',

            # 网络与安全
            '计算机网络', 'TCP/IP', '网络安全', '密码学',

            # 软件工程
            '软件工程', '设计模式', '敏捷开发', 'Git',

            # 大数据
            '大数据', 'Hadoop', 'Spark', '数据挖掘',
        ]
        self.chunk_size = chunk_size
    def fetch_article(self, title: str) -> Tuple[str, str]:
        """
        获取单篇Wikipedia文章

        Args:
            title: 文章标题


        Returns:
            (标题, 内容) 或 (None, None) 如果文章不存在
        """
        page = self.wiki.page(title)

        if not page.exists():
            return None, None

        # 获取文章文本
        text = page.text

        # 基本过滤
        if len(text) < 200:  # 太短的文章跳过
            return None, None

        # 过滤消歧义页面
        if '消歧义' in title or '消歧义' in text[:100]:
            return None, None

        # 过滤列表页面
        if title.startswith('列表:') or title.startswith('索引:'):
            return None, None

        return title, text

    def fetch_multiple_articles(self, topics: List[str], max_articles: int = 50) -> List[Dict]:
        """
        批量获取文章

        Args:
            topics: 主题列表
            max_articles: 最大文章数

        Returns:
            文章列表 [{'title': ..., 'text': ...}, ...]
        """
        articles = []
        fetched_titles = set()

        print(f"\n开始获取Wikipedia文章（目标: {max_articles}篇）...")

        with tqdm(total=max_articles) as pbar:
            for topic in topics:
                if len(articles) >= max_articles:
                    break

                # 获取主文章
                title, text = self.fetch_article(topic)

                if title and title not in fetched_titles:
                    articles.append({'title': title, 'text': text})
                    fetched_titles.add(title)
                    pbar.update(1)

                    if len(articles) < max_articles:
                        related = self._get_related_articles(topic, max_related=3)
                        for rel_title in related:
                            if len(articles) >= max_articles:
                                break

                            rel_title_str, rel_text = self.fetch_article(rel_title)
                            if rel_title_str and rel_title_str not in fetched_titles:
                                articles.append({'title': rel_title_str, 'text': rel_text})
                                fetched_titles.add(rel_title_str)
                                pbar.update(1)

        print(f"✓ 成功获取 {len(articles)} 篇文章")
        return articles

    def _get_related_articles(self, title: str, max_related: int = 3) -> List[str]:

        page = self.wiki.page(title)

        if not page.exists():
            return []

        # 获取页面链接（限制数量）
        links = list(page.links.keys())[:max_related]
        return links

    def clean_text(self,text):
        text = text.strip()
        # metadata_markers = ['參見', '参见', '註釋', '注释', '參考資料',
        #                     '参考资料',
        #                     '外部連結', '外部链接', '延伸閱讀', '延伸阅读']
        # min_pos = len(text)
        # for marker in metadata_markers:
        #     pos = text.find(marker)
        #     if pos != -1 and pos < min_pos:
        #         min_pos = pos
        # if min_pos < len(text):
        #     text = text[:min_pos]
        text = re.sub(r'\{\\displaystyle.*?\}', '', text)
        text = re.sub(r'==+.*?==+', '', text)
        text = re.sub(r'\\\w+','',text)
        text = re.sub(r'\s+',' ',text)
        #{{.*?}},'.'就是任意字符，'*'就是任意次数,?就是不做贪婪
        text = re.sub(r'\{\{.*?\}\}', '', text)
        #这里就是把[[或者]]给去掉的
        text = re.sub(r'\[\[|\]\]', '', text)
        #[d+]这里就是里面如果是数字的话，把数字给去掉的，d+就是去掉连续的数字
        text = re.sub(r'\[(\d+)\]','',text)
        return text
    def chunk_by_text(self,text):
        doc = self.nlp(text)
        chunks = []
        current_chunk =[]
        word_count = 0
        for token in doc:
            #保留格式
            current_chunk.append(token.text_with_ws)
            #不是占位符或者标点
            if not token.is_space and not token.is_punct:
                word_count +=1
                if word_count >=self.chunk_size:
                    chunks.append(''.join(current_chunk).strip())
                    current_chunk = []
                    word_count = 0
        if current_chunk:
            chunks.append(''.join(current_chunk).strip())
        return chunks

if __name__ == '__main__':
    wiki = WikipediaFetcher()
    #articles=wiki.fetch_multiple_articles(topics=wiki.tech_topics)
    # with open('save_path/wiki_articles.jsonl','w',encoding='utf-8') as f:
    #     for article in articles:
    #         #这里主要是为了加入'\n'，所以这里用f.write写入，否则就都混到一块去了
    #         f.write(json.dumps(article,ensure_ascii=False)+'\n')
    path = str(KB_SAVE_PATH_DIR / 'wiki_articles.jsonl')
    path_ext = str(KB_SAVE_PATH_DIR / 'wiki_exact_art.jsonl')
    result_json=[]
    # with open(path,'r',encoding='utf-8') as f:
    #     articles = [json.loads(line)for line in f]
    #     for i in articles:
    #         ext_title = wiki.clean_text(i['title'])
    #         ext_text = wiki.clean_text(i['text'])
    #         result_json.append({'title':ext_title,'ext_text':ext_text})
    # with open(save_path/'wiki_exact_art.jsonl','w',encoding='utf-8') as f:
    #     for article in result_json:
    #         f.write(json.dumps(article,ensure_ascii=False)+'\n')

    with open(path_ext, 'r', encoding='utf-8') as f:
        articles = [json.loads(i)for i in f]
        corpus = []
        chunk_id = 0
        for i in articles:
            title = i['title']
            text = i['ext_text']
            chunks = wiki.chunk_by_text(text)
            for chunk in chunks:
                if len(chunk) >50:
                    corpus.append({
                        'id':chunk_id,
                        'title':f'{title}',
                        'contents':chunk
                    })
                    chunk_id +=1
            print(f'生成{len(chunks)}个chunks')
    json_chunk = save_path / 'wiki_chunk.jsonl'
    with open(json_chunk,'w',encoding='utf-8') as f:
        for i in corpus:
            f.write(json.dumps(i,ensure_ascii=False)+'\n')


