from llama_index.core import StorageContext, load_index_from_storage
from src.insurance_qa.chat_engine import get_chat_engine

async def search_documents(query: str) -> str:
    """
    當客戶詢問關於保險條款、承保範圍、不保事項、理賠流程、或費率表時，請調用此工具。
    此工具會根據最新的保險契約 PDF 提供精準的分析。
    """
    # 注意：這裡需要先取得 index。
    # 建議在啟動時就初始化 index，避免每次 search 都重新讀取磁碟
    try:
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        index = load_index_from_storage(storage_context)
        # 獲取我們精心調教過的 Rerank Query Engine
        engine = get_chat_engine(index)
        
        # 使用 aquery 進行非同步查詢
        response = await engine.aquery(query)
        return str(response)
    except Exception as e:
        return f"檢索條款時發生錯誤: {str(e)}"
