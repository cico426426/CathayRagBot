from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from src.insurance_qa.chat_engine import get_chat_engine
from src.insurance_qa.policy_index import save_or_load_index

async def search_documents(query: str, rule_type: str = None) -> str:
    """
    當客戶詢問關於保險條款、承保範圍、不保事項、理賠流程、或費率表時，請調用此工具。
    此工具會根據最新的保險契約 PDF 提供精準的分析。

    參數：
    - query: 使用者的查詢字串。
    - rule_type: 可選，若查詢涉及特定主題，請傳入對應標籤以加速檢索。
        - '不保事項': 詢問不可理賠、除外責任、拒賠情況。
        - '承保範圍': 詢問理賠項目、賠什麼、賠多少。
        - '理賠文件': 詢問理賠應備文件、證明單據。
        - '用詞定義': 詢問條約中的專有名詞解釋。
    """
    try:
        # 使用封裝好的函數來取得或建立 index
        index = save_or_load_index()
        
        # 根據 Agent 的指示動態建立過濾器
        filters = None
        if rule_type:
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key="rule_type", value=rule_type)]
            )

        # 獲取我們精心調教過的 Rerank Query Engine
        engine = get_chat_engine(index, filters=filters)
        
        # 使用 aquery 進行非同步查詢
        response = await engine.aquery(query)
        
        # 取得 LLM 的主要回答
        final_text = str(response)
        
        # 附加檢索到的原文段落 (Source Nodes) 以供 UI 獨立提取
        sources_text = "===SOURCES_START===\n"
        if hasattr(response, 'source_nodes') and response.source_nodes:
            for idx, node in enumerate(response.source_nodes):
                article = node.metadata.get('article', f'段落 {idx+1}')
                score = f"{node.score:.4f}" if node.score is not None else "N/A"
                text_preview = node.text.strip().replace("\n", " ") if node.text else ""
                if len(text_preview) > 200:
                    text_preview = text_preview[:200] + "..."
                
                sources_text += f"{idx+1}. **【{article}】** (相似度: {score})\n   > _{text_preview}_\n"
        else:
            sources_text += "未找到明確的參考來源。\n"
        sources_text += "===SOURCES_END==="
            
        # 這裡回傳給 Agent 的內容包含 [回答] + [隱藏的來源標籤]
        return f"{final_text}\n\n{sources_text}"
    except Exception as e:
        return f"檢索條款時發生錯誤: {str(e)}"

