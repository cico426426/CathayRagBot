import re
from typing import List
from llama_index.core.schema import TextNode
from llama_index.readers.docling import DoclingReader

def extract_nodes_from_pdf(file_path: str) -> List[TextNode]:
    # 1. 初始化 Docling 讀取器
    reader = DoclingReader()
    # 2. 載入 PDF
    documents = reader.load_data(file_path)
    full_text = documents[0].text
    
    # 2. 定義切分邏輯
    # 我們利用 Regex 尋找「第幾條」、「附表」作為切分點。
    # (?=\n第[一二三四五六七八九十百]+條\s|附表) 代表在「第X條」前面切開，但保留「第X條」這幾個字。
    split_pattern = r'(?=\n(?:#{1,6}\s*)?(?:\*\*)?(?:第[一二三四五六七八九十百]+條|附表))'
    
    chunks = re.split(split_pattern, full_text)
    
    nodes = []
    # current_chapter = "第一章 共同條款"
    current_chapter = ""
    
    for chunk in chunks:
        text_content = chunk.strip()
        if not text_content: continue
        
        # 提取章節標題
        chapter_match = re.search(r'第[一二三四五六七八九十]+章\s*([^\n\r]+)', text_content)
        if chapter_match:
            current_chapter = chapter_match.group(0).replace('#', '').replace('*', '').strip()

        # 提取條文標題與條文名稱
        article_match = re.search(r'(第[一二三四五六七八九十百]+條)\s*([^\n\r]*)', text_content)
        
        # 提取附表標題
        table_match = re.search(r'附表\s*([^\n\r]*)', text_content)
        
        article_title = ""
        rule_type = "一般條款"
        
        if article_match:
            article_label = article_match.group(1).strip()
            article_title = article_match.group(2).strip()
            
            # 依據標題推論條文類型 (rule_type)
            if "不保" in article_title or "除外" in article_title:
                rule_type = "不保事項"
            elif "承保範圍" in article_title:
                rule_type = "承保範圍"
            elif "理賠文件" in article_title:
                rule_type = "理賠文件"
            elif "定義" in article_title:
                rule_type = "用詞定義"
            else:
                rule_type = "一般條款"
                
        elif table_match:
            article_label = table_match.group(0).replace('#', '').strip()
            current_chapter = "附件/費率表" # 附表通常不屬於最後一個章節
            rule_type = "附表"
            article_title = article_label
        else:
            article_label = "前言/其他"
            rule_type = "其他"

        node = TextNode(
            text=text_content,
            metadata={
                "chapter": current_chapter,
                "article": article_label,
                "article_title": article_title,
                "rule_type": rule_type,
                "file_name": file_path.split("/")[-1]
            }
        )
        node.metadata_template = "{key}: {value}"
        node.text_template = "【法規來源：{metadata_str}】\n條文內容：\n{content}"
        nodes.append(node)
        
    print(f"✅ 解析完成：共切分為 {len(nodes)} 個節點（含附表）。")
    return nodes

import json
# 測試用代碼 (可直接執行此檔案確認結果)
if __name__ == "__main__":
    # 執行解析
    test_nodes = extract_nodes_from_pdf("data/海外旅行不便險條款-2.pdf")
    
    # 將結果轉換為易讀的 list 格式
    debug_data = []
    for i, node in enumerate(test_nodes):
        debug_data.append({
            "node_index": i,
            "metadata": node.metadata,
            "text_preview": node.text[:200]  # 只看前 200 字確認切分點
        })
    
    # 存成 debug_nodes.json 
    with open("debug_nodes.json", "w", encoding="utf-8") as f:
        json.dump(debug_data, f, ensure_ascii=False, indent=2)
        
    print(f"📂 詳細切分結果已儲存至: debug_nodes.json")
    
    # 如果還是只有 2 個，我們印出前 500 字來觀察格式
    if len(test_nodes) <= 2:
        print("\n⚠️ 偵測到切分數量過少，以下為原始文本前 500 字，請觀察『第X條』的出現規律：")
        # 這裡需要重新抓一次全文來觀察
        from llama_index.readers.docling import DoclingReader
        doc = DoclingReader().load_data("data/海外旅行不便險條款-2.pdf")
        print(doc[0].text[:500])