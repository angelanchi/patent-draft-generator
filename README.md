# Patent Draft Generator

Side project, 2026-01.

> All examples use a **fictional invention** (a soil-moisture-aware plant watering device).
> No real patent disclosure is included.

## Starting point

Engineers who have an invention often stall at the first draft of the patent
application. I wanted to try whether a structured form plus an LLM could produce a
first draft in the standard six-section format, for a patent attorney to edit.

## What I noticed

- A draft can only be as specific as its inputs, so the form asks separately for the
  technical description, product structure, working principle, prior art and the
  problems to solve.
- Different sections need different prompts; generating them one at a time lets a
  weak section be regenerated without redoing the rest.
- Model providers change quickly, so the code should not depend on one vendor.

## Tools I built

```
form (structured inputs) ──► validation ──► prompt builder ──► LLM adapter ──► section drafts ──► .docx
                                                               │
                                        OpenAI · Claude · Gemini · Qwen
```

- `app/services/llm/` — one `BaseLLMAdapter` and a registry-based `LLMFactory`;
  adding a provider means adding one adapter class.
- `app/utils/prompts.py` — one prompt per section.
- `app/services/validation_service.py` — input checks before any API call.
- `.docx` export with python-docx; Procfile, Render and Railway configs for deployment.

| Layer | Stack |
|---|---|
| Web | Flask, Jinja2, vanilla JS |
| LLM | OpenAI, Anthropic Claude, Google Gemini, Qwen |
| Output | python-docx |

---

## 中文說明


AI驅動的中國專利申請文件自動生成系統，使用OpenAI GPT-4自動生成專業的專利申請文件。

## 功能特點

- **AI智能生成**: 使用OpenAI GPT-4自動生成專業的專利文件內容
- **標準格式**: 遵循中國專利申請文件的標準6章節結構
- **Web界面**: 提供友好的Web界面供用戶輸入信息
- **Word輸出**: 生成格式化的Word文檔(.docx)
- **成本優化**: 智能選擇GPT-3.5或GPT-4模型以優化成本

## 專利文件結構

系統生成包含以下6個章節的完整專利文件：

1. **技術領域** - 說明發明所屬技術領域
2. **背景技術** - 現有技術問題與挑戰
3. **發明內容** - 核心創新點與技術方案
4. **附圖說明** - 圖表描述（如有提供）
5. **具體實施方式** - 詳細實施規格與步驟
6. **其它發明附件** - 支持資訊與元數據

## 系統要求

- Python 3.9 或更高版本
- OpenAI API密鑰
- 至少2GB可用內存
- 穩定的網絡連接

## 快速開始

### 1. 克隆或下載項目

```bash
cd IP-generator
```

### 2. 創建虛擬環境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 配置環境變量

複製 `.env.example` 為 `.env` 並填入您的配置：

```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

編輯 `.env` 文件，填入您的OpenAI API密鑰：

```env
OPENAI_API_KEY=your_actual_api_key_here
SECRET_KEY=your_secret_key_for_flask
```

### 5. 運行應用

```bash
python run.py
```

應用將在 `http://127.0.0.1:5000` 啟動。

## 項目結構

```
IP-generator/
├── app/
│   ├── __init__.py              # Flask應用工廠
│   ├── config.py                # 配置管理
│   ├── routes/
│   │   ├── main.py              # Web路由
│   │   ├── api.py               # REST API
│   │   └── download.py          # 下載處理
│   ├── services/
│   │   ├── ai_service.py        # OpenAI API整合
│   │   ├── patent_generator.py # 專利生成邏輯
│   │   └── document_service.py # Word文檔生成
│   ├── models/
│   │   └── patent_schema.py    # 數據模型
│   ├── templates/               # HTML模板
│   ├── static/                  # CSS/JS/圖片
│   └── utils/
│       └── prompts.py           # AI提示模板
├── templates/
│   └── patent_template.docx    # Word模板
├── output/                      # 生成的文檔
├── uploads/                     # 用戶上傳文件
├── tests/                       # 測試文件
├── requirements.txt             # Python依賴
├── run.py                       # 應用入口
└── README.md                    # 本文件
```

## API端點

### Web界面

- `GET /` - 首頁（專利生成表單）
- `GET /about` - 關於頁面
- `GET /health` - 健康檢查

### REST API

- `POST /api/generate/section` - 生成單個章節
  ```json
  {
    "section_name": "technical_field",
    "patent_data": {
      "patent_name": "...",
      "keywords": "...",
      "technical_description": "..."
    }
  }
  ```

- `POST /api/validate/input` - 驗證輸入數據

### 下載

- `GET /download/patent/<filename>` - 下載生成的專利文件
- `GET /download/list` - 列出所有可下載文件

## 使用示例

### 通過API生成章節

```python
import requests

# API端點
url = "http://127.0.0.1:5000/api/generate/section"

# 請求數據
data = {
    "section_name": "technical_field",
    "patent_data": {
        "patent_name": "一種盆栽自動澆水方法",
        "keywords": "自動澆水, 土壤濕度感測, 盆栽",
        "technical_description": "本發明涉及一種依土壤濕度自動澆水的方法..."
    }
}

# 發送請求
response = requests.post(url, json=data)
result = response.json()

print(f"生成成功: {result['success']}")
print(f"章節內容: {result['content']}")
```

## 配置說明

### 環境變量

| 變量名 | 說明 | 默認值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密鑰 | 必填 |
| `OPENAI_MODEL` | 默認AI模型 | gpt-4-turbo |
| `OPENAI_MAX_TOKENS` | 最大生成token數 | 2000 |
| `OPENAI_TEMPERATURE` | AI創造性參數(0-1) | 0.7 |
| `SECRET_KEY` | Flask密鑰 | 必填 |
| `FLASK_ENV` | 環境(development/production) | development |
| `OUTPUT_DIR` | 輸出目錄 | output |
| `UPLOAD_DIR` | 上傳目錄 | uploads |
| `MAX_UPLOAD_SIZE` | 最大上傳大小(bytes) | 10485760 (10MB) |

### 模型選擇策略

系統自動為不同章節選擇最適合的模型：

- **GPT-3.5-turbo** (成本優化)
  - 技術領域
  - 附圖說明
  - 其它發明附件

- **GPT-4-turbo** (高質量)
  - 背景技術
  - 發明內容
  - 具體實施方式

## 開發指南

### 運行測試

```bash
pytest tests/
```

### 代碼格式化

```bash
black app/
```

### 代碼檢查

```bash
flake8 app/
```

## 成本估算

基於OpenAI的定價（2024年價格）：

- **GPT-3.5-turbo**: ~$0.001-0.003 每章節
- **GPT-4-turbo**: ~$0.01-0.05 每章節
- **完整文件**: ~$0.10-0.20

實際成本取決於輸入長度和生成內容的複雜度。

## 故障排除

### 常見問題

#### 1. OpenAI API調用失敗

```
錯誤: OpenAI API調用失敗
解決: 檢查API密鑰是否正確，確保有足夠的配額
```

#### 2. 模塊導入錯誤

```
錯誤: ModuleNotFoundError
解決: 確保已激活虛擬環境並安裝所有依賴: pip install -r requirements.txt
```

#### 3. 文件編碼問題

```
錯誤: UnicodeEncodeError
解決: 確保系統支持UTF-8編碼，Windows用戶可能需要設置環境變量: set PYTHONIOENCODING=utf-8
```

## 注意事項

1. **API密鑰安全**: 切勿將API密鑰提交到版本控制系統
2. **成本控制**: 設置OpenAI API使用限額以避免意外費用
3. **法律審查**: AI生成的專利文件僅供參考，正式申請前請諮詢專利律師
4. **質量檢查**: 生成後請仔細審查內容的準確性和專業性

## 後續開發計劃

- [ ] 完整的Web界面（多步驟表單）
- [ ] 文檔生成服務（document_service.py）
- [ ] 專利生成器服務（patent_generator.py）
- [ ] 批量生成功能
- [ ] 用戶認證系統
- [ ] 歷史記錄和版本控制
- [ ] PDF輸出支持
- [ ] 多語言支持（英文專利）

## 技術棧

- **後端框架**: Flask 3.0
- **AI服務**: OpenAI API (GPT-4 / GPT-3.5-turbo)
- **文檔生成**: python-docx
- **數據驗證**: Pydantic
- **日誌**: Loguru
- **重試邏輯**: Tenacity

## 貢獻

歡迎提交Issue和Pull Request！

## 授權

本項目僅供學習和研究使用。

## 聯絡方式

如有問題或建議，請通過以下方式聯繫：

- Email: [待補充]
- GitHub Issues: [待補充]

---

**免責聲明**: 本工具生成的專利文件僅供參考。正式申請專利前，請務必諮詢專業的專利律師或代理人。
