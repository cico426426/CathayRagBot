import os
import sys
import time
import numpy as np
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.insurance_qa.policy_index import save_or_load_index
from src.insurance_qa.chat_engine import get_chat_engine

from trulens.core import TruSession, Feedback
from trulens.apps.llamaindex import TruLlama
from trulens.providers.openai import OpenAI

load_dotenv()

def main():
    print("🚀 正在初始化 RAG 引擎...")
    try:
        index = save_or_load_index()
    except Exception as e:
        print(f"❌ 載入索引失敗: {e}")
        return

    query_engine = get_chat_engine(index)

    # ─── 🔑 關鍵除錯：確認引擎類型 ───────────────────────────────────
    print(f"🔍 引擎類型: {type(query_engine)}")

    print("📊 正在設定 TruLens 評估指標...")
    session = TruSession()
    session.reset_database()

    provider = OpenAI(model_engine="gpt-4o-mini")

    # ─── 🔑 修正 2：select_context 必須在確認引擎類型後才呼叫 ──────────
    context = TruLlama.select_context(query_engine)

    # ─── 🔑 修正 3：用 on_context() 作為備援寫法（更穩定） ─────────────
    # 如果 select_context 路徑不對，改用 .on_context(collect_list=True/False)
    # .on_context(collect_list=True)  → 給 Groundedness 用（需要 list）
    # .on_context(collect_list=False) → 給 Context Relevance 用（逐筆評分）

    f_groundedness = (
        Feedback(
            provider.groundedness_measure_with_cot_reasons,
            name="Groundedness"
        )
        .on_context(collect_list=True)
        .on_output()
    )

    f_answer_relevance = (
        Feedback(
            provider.relevance_with_cot_reasons,
            name="Answer Relevance"
        )
        .on_input_output()
    )

    f_context_relevance = (
        Feedback(
            provider.context_relevance_with_cot_reasons,
            name="Context Relevance"
        )
        .on_input()
        .on_context(collect_list=False)
        .aggregate(np.mean)
    )

    feedbacks = [f_groundedness, f_answer_relevance, f_context_relevance]

    tru_recorder = TruLlama(
        query_engine,
        app_name="Cathay_RAG_Bot",
        app_version="v2",
        feedbacks=feedbacks
    )

    test_questions = [
        "班機延誤多久才會有理賠？",
        "如果遇到恐怖主義行為，這份保單會賠嗎？",
        "投保 14 天的費率係數是多少？",
        "行李遺失最多可以賠多少錢？"
    ]

    print("🏃 正在執行自動化測試...")
    for question in test_questions:
        print(f"\n💬 測試問題: {question}")
        with tru_recorder as recording:
            response = query_engine.query(question)
        print(f"🤖 AI 回答: {str(response)[:100]}...")

        # ─── 🔑 修正 4：每題跑完立刻等待該筆 feedback 計算完成 ──────────
        # 這樣可以避免所有題目同時觸發 OpenAI API 造成 rate limit
        print("⏳ 等待此題評分完成...")
        try:
            session.wait_for_feedback_results()
        except Exception as e:
            print(f"  ⚠️ 評分等待例外: {e}")

        # ─── 🔑 修正 5：評分完後再等 15 秒（不是 10 秒）避免下一題 rate limit
        print("😴 暫停 15 秒...")
        time.sleep(15)

    print("\n✅ 所有測試完成！")

    from trulens.dashboard import run_dashboard
    print("🌐 正在啟動 TruLens Dashboard...")
    run_dashboard(session=session, port=8501)

if __name__ == "__main__":
    main()