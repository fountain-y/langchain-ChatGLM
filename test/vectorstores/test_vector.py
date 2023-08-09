import sys
sys.path.append('/home/yuanrz/projects/langchain-ChatGLM')
print(sys.path)

from configs.model_config import *
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import nltk
from vectorstores import MyFAISS
from chains.local_doc_qa import load_file

from chains.local_doc_qa import load_vector_store, LocalDocQA

nltk.data.path = [NLTK_DATA_PATH] + nltk.data.path

if __name__ == "__main__":
    vs_path = '/home/yuanrz/projects/langchain-ChatGLM/knowledge_base/financial/vector_store'
    localdocqA = LocalDocQA()
    localdocqA.init_cfg()
    query = '证券公司分类如何实施? 用中文详细说明每个步骤'
    
    vector_store = load_vector_store(vs_path, localdocqA.embeddings)
    vector_store.chunk_size = localdocqA.chunk_size
    vector_store.chunk_conent = localdocqA.chunk_conent
    vector_store.score_threshold = localdocqA.score_threshold
    
    import pdb;pdb.set_trace()
    related_docs_with_score = vector_store.similarity_search_with_score(query, k=localdocqA.top_k)
    
    print(related_docs_with_score)
    print('finish!')
    pass