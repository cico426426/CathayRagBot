import os
import sys

import gradio as gr
from src.insurance_qa.policy_parser import extract_nodes_from_pdf
from src.insurance_qa.policy_index import save_or_load_index
from src.insurance_qa.chat_engine import get_chat_engine
def launch_app():
    # 1. 準備資料 (如果沒有 index 就跑 ingestion)
    # 這裡假設你的 PDF 放在 data/ 目錄下
    pdf_path = "data/海外旅行不便險條款-2.pdf"
    
    try:
        # 嘗試加載，若失敗則建立
        try:
            index = save_or_load_index()
        except:
            nodes = extract_nodes_from_pdf(pdf_path)
            index = save_or_load_index(nodes)
            
        query_engine = get_chat_engine(index)
        
        # 2. 定義 Gradio 互動邏輯
        def predict(message, history):
            response = query_engine.query(message)
            
            # 取得 LLM 的主要回答
            final_text = str(response)
            
            # 附加檢索到的原文段落 (Source Nodes) 以供驗證
            sources_text = "\n\n---\n### 💡 檢索證據 (RAG 參考的原始條文):\n"
            if hasattr(response, 'source_nodes'):
                for idx, node in enumerate(response.source_nodes):
                    # 嘗試取得 metadata 中的條號 (若無則顯示未知)
                    article = node.metadata.get('article', f'段落 {idx+1}')
                    score = f"{node.score:.4f}" if node.score is not None else "N/A"
                    # 擷取部分文字作為預覽
                    text_preview = node.text+"\n" if node.text else ""
                    
                    sources_text += f"- **【{article}】** (相似度: {score})\n  > _{text_preview}_\n"
            else:
                sources_text += "未找到參考來源。\n"
                
            return final_text + sources_text

        # 3. 啟動介面
        demo = gr.ChatInterface(
            fn=predict,
            title="🛡️ 國泰產險 RAG 條款助理",
            description="請輸入您的問題，我將根據保險條文為您解答（例如：班機延誤幾小時會賠？）",
            examples=["什麼情況下可以申請旅遊延誤賠償？", "行李遺失後應該如何申請理賠？", "哪些原因屬於不可理賠範圍？", "如果我在旅途中生病了，保險會賠嗎？"]
        )
        demo.launch(share=False)
        
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

if __name__ == "__main__":
    launch_app()

