# 🛡️ 國泰產險保險問答助理 (CathayRagBot)

這是一個基於 **LlamaIndex** 與 **Gradio** 開發的 RAG (Retrieval-Augmented Generation) 系統，專門用於解答國泰海外旅行不便險的條款內容。

## 🚀 專案特點

- **領域驅動架構 (Screaming Architecture)**：專注於「保險問答」領域，直觀反映系統商業價值。
- **高效檢索**：使用 LlamaIndex 結合 OpenAI 進行語義搜尋。
- **條款重排**：內建 LLM Reranker，提升回答精準度。
- **Gradio 介面**：提供親切的對話框介面，並在回答後附上條文來源證明。
- **自動化評估**：整合 **TruLens**，針對 Groundedness (根據性)、Relevance (關聯性) 進行 AI 自動化測試。

## 📂 檔案結構

```text
CathayRagBot/
├── app.py              # Gradio 應用程式入口點 (主要啟動程式)
├── test_insurance_qa.py # TruLens 自動化測試與評估腳本
├── pyproject.toml      # 專案依賴設定 (使用 uv)
├── src/
│   └── insurance_qa/   # 📢 保險問答核心領域模組
│       ├── chat_engine.py      # 查詢引擎與聊天邏輯設定
│       ├── policy_parser.py    # PDF 解析與條款文件切分 (使用 Docling)
│       ├── prompts.py          # RAG 回答模組的 Prompt 設定
│       └── policy_index.py     # 向量資料庫儲存與載入
├── data/               # 存放 PDF 條款原始檔
└── storage/            # 存放建置好的向量索引 (Index)
```

## 🛠️ 安裝與啟動

### 1. 環境準備
本專案建議使用 [uv](https://github.com/astral-sh/uv) 進行管理。請先在根目錄建立 `.env` 檔案並填入你的 API Key：
```text
OPENAI_API_KEY=your_api_key_here
```

### 2. 安裝依賴
```bash
uv sync
```

### 3. 啟動對話介面
```bash
uv run python app.py
```
啟動後，開啟瀏覽器進入 `http://127.0.0.1:7860` 即可開始使用。

### 4. 執行品質測試
```bash
uv run python test_insurance_qa.py
```
測試完成後會啟動 TruLens Dashboard (預設 Port 8501)，可查看回答的品質指標。

## ⚠️ 目前系統限制

本專案目前為原型開發階段 (PoC)，尚有以下限制：

- **缺乏對話記憶 (Stateless)**：目前的問答引擎是基於 `QueryEngine` 實作，不具備多輪對話的記憶能力。每一筆提問都會被視為獨立事件，無法參考先前的對話上下文。
- **尚未實作防護欄 (No Guardrails)**：系統目前僅專注於 RAG 檢索準確度，尚未整合內容安全防護機制（如 NeMo Guardrails 或 Llama Guard）。系統可能會回答與保險條款無關的問題，或無法過濾敏感資訊。
- **單一文件來源**：目前僅針對單一 PDF 文件進行優化，若要擴展至多份複雜文件，可能需要調整索引結構。

## 📝 開發說明
- **解析器**：使用 `DoclingReader` 處理 PDF，能精準辨識條款層級。
- **索引方式**：採用 `VectorStoreIndex` 並持久化於 `storage/` 目錄。
- **重排器**：使用 `LLMRerank` 確保最相關的條文段落排在最前面。
