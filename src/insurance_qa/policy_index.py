import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from typing import List
from llama_index.core.schema import TextNode
from dotenv import load_dotenv

load_dotenv()

# 設定存儲路徑
STORAGE_DIR = "./storage"

def save_or_load_index(nodes: List[TextNode] = None):
    # 如果已經有儲存好的索引，直接讀取
    if os.path.exists(STORAGE_DIR) and os.listdir(STORAGE_DIR):
        print("📁 發現既有索引，正在從本地讀取...")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
    else:
        # 如果沒有，則根據傳入的 nodes 建立新索引
        if nodes is None:
            print("⚠️ 找不到既有索引，自動從 PDF 解析建立新索引...")
            from src.insurance_qa.policy_parser import extract_nodes_from_pdf
            nodes = extract_nodes_from_pdf("data/海外旅行不便險條款-2.pdf")
            
        print("⚡ 正在建立新索引並計算向量（Embedding）...")
        index = VectorStoreIndex(nodes)
        
        # 將索引存到磁碟中
        print(f"💾 正在將索引儲存至 {STORAGE_DIR}...")
        index.storage_context.persist(persist_dir=STORAGE_DIR)
        
    return index

# 測試用
if __name__ == "__main__":
    # 這裡可以串接 ingestion.py 的結果
    from ingestion import extract_nodes_from_pdf
    nodes = extract_nodes_from_pdf("data/海外旅行不便險條款-2.pdf")
    index = save_or_load_index(nodes)

    # 建立查詢引擎
    query_engine = index.as_query_engine()

    # 進行查詢
    response = query_engine.query("什麼情況下可以申請班機延誤險？，用繁體中文回答")
    print(response)