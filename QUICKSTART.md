# 快速入門指南

## 5分鐘快速設置

### 步驟 1: 安裝依賴

```bash
# 創建虛擬環境（Windows）
python -m venv venv
venv\Scripts\activate

# 安裝所有依賴
pip install -r requirements.txt
```

### 步驟 2: 配置API密鑰

創建 `.env` 文件（複製 `.env.example`）:

```bash
copy .env.example .env
```

編輯 `.env` 文件，填入您的 OpenAI API 密鑰：

```env
# 必填 - OpenAI API密鑰
OPENAI_API_KEY=sk-your-actual-api-key-here

# 必填 - Flask密鑰（可以是任意隨機字符串）
SECRET_KEY=your-random-secret-key-here

# 可選 - 其他配置使用默認值即可
OPENAI_MODEL=gpt-4-turbo
FLASK_ENV=development
```

**重要**: 獲取 OpenAI API 密鑰:
1. 訪問 https://platform.openai.com/api-keys
2. 登入或註冊賬號
3. 點擊 "Create new secret key"
4. 複製密鑰並粘貼到 `.env` 文件中

### 步驟 3: 啟動應用

```bash
python run.py
```

應用將在 http://127.0.0.1:5000 啟動

### 步驟 4: 測試系統

在另一個終端窗口運行測試腳本：

```bash
# 激活虛擬環境
venv\Scripts\activate

# 運行測試
python test_patent_generation.py
```

## 快速測試 API

### 1. 測試健康狀態

```bash
curl http://127.0.0.1:5000/api/test
```

### 2. 生成單個章節（技術領域）

創建 `test_request.json`:

```json
{
  "section_name": "technical_field",
  "patent_data": {
    "patent_name": "一種盆栽自動澆水方法",
    "keywords": "自動澆水, 土壤濕度感測",
    "technical_description": "本發明涉及一種依土壤濕度自動澆水的方法..."
  }
}
```

發送請求：

```bash
curl -X POST http://127.0.0.1:5000/api/generate/section \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### 3. 生成完整專利文件

創建 `full_patent_request.json`:

```json
{
  "patent_name": "一種具土壤濕度感測之盆栽自動澆水裝置及方法",
  "inventors": "張三、李四",
  "keywords": "自動澆水, 土壤濕度感測, 盆栽, 微控制器",
  "technical_description": "本發明涉及園藝自動化技術領域，特別是一種依土壤濕度自動澆水的盆栽裝置...",
  "product_info": "裝置包括土壤濕度感測器、微控制器、微型水泵...",
  "working_principle": "微控制器定時讀取土壤濕度，低於門檻時啟動水泵..."
}
```

發送請求：

```bash
curl -X POST http://127.0.0.1:5000/api/generate/patent \
  -H "Content-Type: application/json" \
  -d @full_patent_request.json
```

## 使用Python腳本測試

```python
import requests

# API地址
API_URL = "http://127.0.0.1:5000/api"

# 測試數據
data = {
    "patent_name": "一種盆栽自動澆水方法",
    "inventors": "張三、李四",
    "keywords": "自動澆水, 土壤濕度感測",
    "technical_description": "本發明涉及盆栽自動澆水技術..."
}

# 生成專利
response = requests.post(
    f"{API_URL}/generate/patent",
    json=data
)

result = response.json()
if result['success']:
    print(f"✅ 生成成功!")
    print(f"文件路徑: {result['file_path']}")
    print(f"總字數: {result['patent_info']['total_word_count']}")
else:
    print(f"❌ 生成失敗: {result['error']}")
```

## 查看生成的文件

生成的 Word 文檔保存在 `output/` 目錄中。

直接打開 `.docx` 文件即可查看完整的專利申請文件。

## 可用的 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/test` | GET | 健康檢查 |
| `/api/validate/input` | POST | 驗證輸入數據 |
| `/api/generate/section` | POST | 生成單個章節 |
| `/api/generate/patent` | POST | 生成完整專利文件 |
| `/api/estimate/cost` | POST | 估算生成成本 |
| `/download/patent/<filename>` | GET | 下載專利文件 |
| `/download/list` | GET | 列出所有文件 |

## 成本估算

- **單個章節**: ~$0.01-0.05 USD
- **完整專利**: ~$0.10-0.20 USD

實際成本取決於輸入內容的複雜度和長度。

## 常見問題

### Q: OpenAI API 調用失敗？

**A**: 檢查以下項目：
1. API 密鑰是否正確
2. OpenAI 賬戶是否有足夠額度
3. 網絡連接是否正常
4. 查看 `logs/app.log` 獲取詳細錯誤信息

### Q: 生成內容質量不理想？

**A**: 嘗試：
1. 提供更詳細的技術描述
2. 增加更多關鍵字
3. 在 `product_info`、`working_principle` 等字段提供更多信息

### Q: 生成速度慢？

**A**:
- 完整專利生成需要調用 6 次 AI API
- 正常耗時約 2-5 分鐘
- 可以在 `.env` 中調整 `OPENAI_MODEL` 使用 `gpt-3.5-turbo` 加快速度（但質量會降低）

### Q: Word 文檔格式問題？

**A**:
- 使用 Microsoft Word 2016 或更高版本打開
- 如果格式有問題，可以在 Word 中手動調整

## 下一步

- 閱讀完整的 [README.md](README.md) 了解更多功能
- 探索 `app/utils/prompts.py` 自定義提示範本

## 需要幫助？

- 查看日誌: `logs/app.log`
- 檢查 GitHub Issues
- 閱讀 OpenAI API 文檔: https://platform.openai.com/docs

---

**提示**: 首次使用建議先運行 `test_patent_generation.py` 測試腳本，逐步測試各項功能！
