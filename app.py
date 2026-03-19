import asyncio
import os
import gradio as gr
from dotenv import load_dotenv

# 從我們定義的 Agent 核心模組匯入
from src.agents.insurance_agent import agent, ctx as agent_ctx

load_dotenv()

def launch_gradio():
    """
    啟動 Gradio 介面，並將其連接至 Insurance Agent。
    """
    # 1. 確保索引已經建立
    print("🔍 檢查並初始化向量資料庫...")
    from src.insurance_qa.policy_index import save_or_load_index
    save_or_load_index()

    # 2. 定義 Gradio 的非同步預測函數
    async def predict(message, history):
        """
        對接 Gradio 的核心預測函數。
        message: 當前用戶輸入。
        history: Gradio 自動維護的對話紀錄。
        """
        try:
            # 調用 Agent 執行任務，傳入持久化的 agent_ctx 以維持記憶
            response = await agent.run(message, ctx=agent_ctx)
            
            # 解析 Agent 生成的專業回答
            final_answer = str(response)
            
            # 從工具執行紀錄中抽取原始來源，讓前端直接渲染，完全不經過 Agent 處理
            sources_list = []
            tool_calls = getattr(response, 'tool_calls', []) or []
            
            for tc in tool_calls:
                # 提早過濾不相關的工具
                if getattr(tc, 'tool_name', '') != 'search_documents':
                    continue
                
                # 安全地獲取工具的原始回傳字串
                raw_out = getattr(getattr(tc, 'tool_output', None), 'raw_output', '')
                
                # 確保來源標記存在
                if "===SOURCES_START===" not in raw_out:
                    continue
                    
                # 擷取並去除頭尾空白
                extracted = raw_out.split("===SOURCES_START===")[1].split("===SOURCES_END===")[0].strip()
                if extracted:
                    sources_list.append(extracted)
            
            if sources_list:
                sources_str = "\n".join(sources_list)
                final_answer += f"\n\n---\n### 🔍 參考證據 (原始條文)\n{sources_str}"
                
            return final_answer
        except Exception as e:
            return f"⚠️ 抱歉，處理您的請求時發生錯誤：{str(e)}"

    # 3. 建立並配置 ChatInterface
    demo = gr.ChatInterface(
        fn=predict,
        title="🛡️ 國泰產險智能 Agent 助理",
        description="我是您的全能保險助理。",
        examples=[
            "什麼情況下可以申請旅遊延誤賠償？",
            "行李遺失後應該如何申請理賠？",
            "哪些原因屬於不可理賠範圍？",
        ]
    )
    
    print("🚀 Gradio 介面已在 http://127.0.0.1:7860 啟動")
    demo.launch(share=False)

if __name__ == "__main__":
    # 啟動 Gradio
    launch_gradio()