import asyncio
from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Context

from src.tools.document_search import search_documents

load_dotenv()

# --- 配置 Agent ---

# 建立 Agent 實例
agent = FunctionAgent(
    tools=[search_documents],
    llm=OpenAI(model="gpt-4o-mini"),
    system_prompt=(
        "你是一位全能的保險服務助理。你可以使用 search_documents 工具查詢保險條約。"
        "如果客戶問到保險相關問題，請務必先查詢條款。"
        "回答時請保持專業且親切。"
    ),
)

# 建立對話上下文（這會持有對話記憶）
ctx = Context(agent)

async def main():
    print("🚀 保險 Agent 已啟動")
    
    # 測試情境：先查條款，再算金額
    questions = [
        "班機延誤理賠是多少錢？",
        "如果我有兩個人，每個人理賠 5000，總共是多少？"
    ]
    
    for q in questions:
        print(f"\n👤 用戶: {q}")
        # 傳入 ctx 確保 agent 記得之前的對話
        response = await agent.run(q, ctx=ctx)
        print(f"🤖 助理: {str(response)}")

if __name__ == "__main__":
    asyncio.run(main())
