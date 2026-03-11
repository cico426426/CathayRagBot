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
        "你是一位全能的保險服務助理。當客戶詢問保險相關問題時，請務必先調用 search_documents 工具查詢條款。\n\n"
        "【回覆規範】\n"
        "1. 請根據檢索到的資訊總結並回答客戶的問題。\n"
        "2. 工具回傳的內容末尾可能包含 `===SOURCES_START===` 與 `===SOURCES_END===` 包覆的來源區塊。**請你完全忽略該區塊，絕不要將這些來源標記或內容包含在你的最終回覆中**。前端介面會獨立負責渲染這些原始證據。\n"
        "3. 你的回答應維持親切、專業、流暢，直接回答問題即可。"
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
