# 🛡️ 國泰產險保險問答助理 (CathayRagBot)

這是一個基於 **LlamaIndex** 與 **Gradio** 開發的 Agentic RAG 系統，專門用於解答國泰海外旅行不便險的條款內容。

## 🚀 專案特點

- **Agentic 系統架構**：採用 `FunctionAgent` 整合檢索工具，能自主決定是否需要查詢條款來回答問題。
- **多輪對話記憶 (Stateful)**：具備對話上下文記憶功能，能根據之前的提問進行連續追問。
- **領域驅動架構 (Screaming Architecture)**：清晰的目錄結構，直觀反映系統「保險問答」的核心功能。
- **高效檢索與重排**：使用 LlamaIndex 結合 OpenAI 進行語義搜尋，並內建 LLM Reranker 提升回答精準度。
- **Gradio 介面**：提供親切的對話框介面，支援範例快速提問。
- **自動化評估**：整合 **TruLens**，針對 Groundedness (根據性)、Relevance (關聯性) 進行 AI 自動化測試。

## 📂 檔案結構

```text
CathayRagBot/
├── app.py              # Gradio 應用程式入口點 (主要啟動程式)
├── test_insurance_qa.py # TruLens 自動化測試與評估腳本
├── pyproject.toml      # 專案依賴設定 (使用 uv)
├── src/
│   ├── agents/         # 🤖 Agent 邏輯與行為配置
│   │   └── insurance_agent.py
│   ├── tools/          # 🛠️ Agent 使用的外部工具 (如文件檢索)
│   │   └── document_search.py
│   └── insurance_qa/   # 📢 保險問答核心檢索模組 (RAG)
│       ├── chat_engine.py      # 查詢引擎與 Rerank 設定
│       ├── policy_parser.py    # PDF 解析與條款切分 (使用 Docling)
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

- **文件結構依賴性**：RAG 的檢索效果高度依賴 `DoclingReader` 對保險條款特定格式的解析規則。若保險條約的排版風格發生劇烈變化（如改為表格密集型 or 非標準標題結構），現有的切分與索引規則可能不再適用。
- **尚未實作內容防護欄 (No Guardrails)**：系統尚未整合內容安全防護機制（如 NeMo Guardrails）。雖然有 System Prompt 約束，但仍可能被誘導回答非保險相關問題。
- **單一文件來源**：目前僅針對單一 PDF 文件進行優化，擴展至多份複雜文件時，檢索的雜訊比可能會提升。

## 📝 開發說明
- **解析器**：使用 `DoclingReader` 處理 PDF，能辨識層級並進行語義塊 (Chunking) 切分。
- **索引方式**：採用 `VectorStoreIndex` 並持久化於 `storage/` 目錄。
- **推理模式**：使用 `gpt-4o-mini` 作為 Agent 的大腦，平衡效能與成本。
