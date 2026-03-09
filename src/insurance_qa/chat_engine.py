from src.insurance_qa.prompts import qa_prompt_tmpl
from llama_index.core import PromptTemplate

from llama_index.core.postprocessor import LLMRerank

qa_prompt = PromptTemplate(qa_prompt_tmpl)

def get_chat_engine(index):
# 使用 LLM 進行重排
    rerank_postprocessor = LLMRerank(
        choice_batch_size=5, 
        top_n=3
    )

    query_engine = index.as_query_engine(
        similarity_top_k=10,
        node_postprocessors=[rerank_postprocessor],
    )
    

    # 3. 更新 Prompt
    qa_prompt = PromptTemplate(qa_prompt_tmpl)    
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": qa_prompt
    })
    
    return query_engine
