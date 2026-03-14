import os
import sys
import time
import numpy as np
from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.insurance_qa.policy_index import save_or_load_index
from src.insurance_qa.chat_engine import get_chat_engine

from trulens.core import Feedback, TruSession
from trulens.apps.llamaindex import TruLlama
from trulens.providers.openai import OpenAI
from trulens.dashboard import run_dashboard


def main():
    print("🚀 正在初始化 RAG 引擎...")
    try:
        index = save_or_load_index()
    except Exception as e:
        print(f"❌ 載入索引失敗: {e}")
        return

    query_engine = get_chat_engine(index)

    print("📊 正在設定 TruLens 評估指標...")
    session = TruSession()
    session.reset_database()
    provider = OpenAI(model_engine="gpt-4o-mini")

    f_groundedness = (
        Feedback(
            provider.groundedness_measure_with_cot_reasons,
            name="Groundedness",
        )
        .on_context(collect_list=True)
        .on_output()
    )

    f_answer_relevance = (
        Feedback(
            provider.relevance_with_cot_reasons,
            name="Answer Relevance",
        )
        .on_input_output()
    )

    f_context_relevance = (
        Feedback(
            provider.context_relevance_with_cot_reasons,
            name="Context Relevance",
        )
        .on_input()
        .on_context(collect_list=False)
        .aggregate(np.mean)
    )

    feedbacks = [f_groundedness, f_answer_relevance, f_context_relevance]
    feedback_names = [feedback.name for feedback in feedbacks]

    tru_recorder = TruLlama(
        query_engine,
        app_name="Cathay_RAG_Bot",
        app_version="v2",
        feedbacks=feedbacks,
    )

    eval_questions = [
        "什麼情況下可以申請旅遊延誤賠償？",
        "行李遺失後應該如何申請理賠？",
        "哪些原因屬於不可理賠範圍？",
    ]

    print("🏃 正在執行自動化測試...")
    for question in eval_questions:
        print(f"\n💬 測試問題: {question}")
        with tru_recorder as recording:
            response = query_engine.query(question)
        record = recording.get()
        print(f"🤖 AI 回答: {str(response)[:100]}...")

        print("⏳ 等待此題評分完成...")
        try:
            session.wait_for_feedback_results(
                record_ids=[record.record_id],
                feedback_names=feedback_names,
                timeout=180,
                poll_interval=0.5,
            )
        except Exception as e:
            print(f"  ⚠️ 評分等待例外: {e}")

        print("😴 暫停 15 秒...")
        time.sleep(15)

    print("\n✅ 所有測試完成！")
    print("🌐 正在啟動 TruLens Dashboard...")
    run_dashboard(session=session, port=8501)


if __name__ == "__main__":
    main()
