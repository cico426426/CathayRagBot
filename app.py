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
            
            # 返回 Agent 生成的專業回答
            return str(response)
        except Exception as e:
            return f"⚠️ 抱歉，處理您的請求時發生錯誤：{str(e)}"

    # 3. 建立並配置 ChatInterface
    demo = gr.ChatInterface(
        fn=predict,
        title="🛡️ 國泰產險智能 Agent 助理",
        description="我是您的全能保險助理。我可以幫您【分析複雜條款】並同時進行【理賠金額計算】。",
        examples=[
            "班機延誤理賠是多少？我有3個人延誤，總共領多少？",
            "行李遺失後應該如何申請理賠？",
            "手機掉在路邊有賠嗎？",
            "如果投保 14 天，費率係數是多少？"
        ]
    )
    
    print("🚀 Gradio 介面已在 http://127.0.0.1:7860 啟動")
    demo.launch(share=False)

if __name__ == "__main__":
    # 啟動 Gradio
    launch_gradio()