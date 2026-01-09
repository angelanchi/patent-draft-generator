# 貢獻指南

感謝您對 AI 專利文件生成器項目的關注！本文檔將指導您如何為項目做出貢獻。

## 目錄

- [開發環境設置](#開發環境設置)
- [代碼規範](#代碼規範)
- [提交流程](#提交流程)
- [測試規範](#測試規範)
- [文檔編寫](#文檔編寫)
- [問題報告](#問題報告)

---

## 開發環境設置

### 前置要求

- Python 3.9 或更高版本
- Git
- OpenAI API 密鑰

### 設置步驟

1. **Fork 並克隆倉庫**

```bash
git clone https://github.com/your-username/IP-generator.git
cd IP-generator
```

2. **創建虛擬環境**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **安裝依賴**

```bash
# 安裝生產依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install black flake8 pytest pytest-cov mypy
```

4. **配置環境變量**

```bash
cp .env.example .env
# 編輯 .env 文件，填入您的配置
```

5. **運行測試**

```bash
pytest tests/
```

6. **啟動開發服務器**

```bash
python run.py
```

---

## 代碼規範

### 重要規則

**請務必閱讀 [CLAUDE.md](CLAUDE.md) 了解完整的開發規範！**

核心原則：

1. **代碼中不使用 Emoji**
   - Emoji 僅用於 HTML 模板和用戶可見的界面
   - Python 代碼、日誌、API 響應中禁止使用 Emoji

2. **遵循 PEP 8**
   - 使用 `black` 格式化代碼
   - 使用 `flake8` 檢查代碼質量

3. **編寫清晰的註釋和文檔**
   - 所有公共函數必須有 docstring
   - 使用 Google 風格的 docstring

4. **類型註解**
   - 盡可能使用類型提示
   - 使用 `mypy` 進行類型檢查

### 代碼格式化

在提交前運行：

```bash
# 格式化代碼
black app/ tests/

# 檢查代碼質量
flake8 app/ tests/

# 類型檢查
mypy app/
```

### 示例代碼

```python
from typing import Dict, List, Optional
from loguru import logger

def generate_section_content(
    section_name: str,
    input_data: Dict[str, str],
    use_recommended_model: bool = True
) -> str:
    """
    生成指定章節的內容

    Args:
        section_name: 章節名稱
        input_data: 輸入數據字典
        use_recommended_model: 是否使用推薦模型

    Returns:
        str: 生成的內容

    Raises:
        ValueError: 當輸入無效時
    """
    logger.info(f"開始生成章節: {section_name}")

    # 實現邏輯
    content = "..."

    return content
```

---

## 提交流程

### 分支策略

- `main`: 主分支，穩定版本
- `develop`: 開發分支
- `feature/功能名`: 功能分支
- `bugfix/問題名`: 修復分支

### 提交步驟

1. **創建功能分支**

```bash
git checkout -b feature/add-pdf-export
```

2. **進行開發**

- 編寫代碼
- 添加測試
- 更新文檔

3. **提交更改**

```bash
git add .
git commit -m "feat: 添加 PDF 導出功能"
```

### Commit Message 規範

使用 Conventional Commits 格式：

```
<類型>(<範圍>): <簡短描述>

[可選的詳細描述]

[可選的註腳]
```

類型：

- `feat`: 新功能
- `fix`: 修復 bug
- `docs`: 文檔更新
- `style`: 代碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 構建/工具相關

範例：

```bash
git commit -m "feat(api): 添加批量生成端點"
git commit -m "fix(validation): 修復字數限制檢查錯誤"
git commit -m "docs: 更新 API 文檔"
git commit -m "refactor(generator): 簡化生成流程邏輯"
```

4. **推送到遠程**

```bash
git push origin feature/add-pdf-export
```

5. **創建 Pull Request**

在 GitHub 上創建 Pull Request：

- 提供清晰的標題和描述
- 列出主要更改
- 關聯相關 Issue
- 等待代碼審查

### Pull Request 模板

```markdown
## 描述

簡要說明本 PR 的內容

## 更改類型

- [ ] 新功能
- [ ] Bug 修復
- [ ] 文檔更新
- [ ] 重構
- [ ] 其他

## 相關 Issue

Closes #123

## 測試

- [ ] 已添加單元測試
- [ ] 已通過所有測試
- [ ] 已手動測試

## 檢查清單

- [ ] 代碼遵循項目規範
- [ ] 已運行 black 格式化
- [ ] 已通過 flake8 檢查
- [ ] 已更新相關文檔
- [ ] Python 代碼中無 Emoji
```

---

## 測試規範

### 測試結構

```
tests/
├── __init__.py
├── conftest.py                 # pytest 配置和 fixtures
├── test_ai_service.py
├── test_patent_generator.py
├── test_document_service.py
└── test_validation_service.py
```

### 編寫測試

```python
import pytest
from app.services.validation_service import ValidationService

@pytest.fixture
def validation_service():
    """創建驗證服務實例"""
    return ValidationService()

def test_validate_patent_input_success(validation_service):
    """測試有效輸入驗證成功"""
    valid_data = {
        'patent_name': '有效的專利名稱',
        'inventors': '張三、李四',
        'keywords': '關鍵字1, 關鍵字2',
        'technical_description': '足夠長的技術描述文本...'
    }

    is_valid, errors = validation_service.validate_patent_input(valid_data)

    assert is_valid is True
    assert len(errors) == 0

def test_validate_patent_input_missing_name(validation_service):
    """測試缺少必填字段時驗證失敗"""
    invalid_data = {
        'inventors': '張三',
        'keywords': '關鍵字',
        'technical_description': '描述'
    }

    is_valid, errors = validation_service.validate_patent_input(invalid_data)

    assert is_valid is False
    assert any('patent_name' in error for error in errors)
```

### 運行測試

```bash
# 運行所有測試
pytest

# 運行特定測試文件
pytest tests/test_validation_service.py

# 運行特定測試函數
pytest tests/test_validation_service.py::test_validate_patent_input_success

# 生成覆蓋率報告
pytest --cov=app --cov-report=html

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s
```

### 測試覆蓋率目標

- 新功能必須有對應測試
- 目標覆蓋率：70% 以上
- 核心模塊（services）覆蓋率：80% 以上

---

## 文檔編寫

### 文檔類型

1. **代碼註釋**
   - 所有公共函數/類必須有 docstring
   - 複雜邏輯需要行內註釋

2. **API 文檔**
   - 更新 README.md 中的 API 端點說明
   - 提供請求/響應示例

3. **用戶文檔**
   - 更新 README.md 或 QUICKSTART.md
   - 添加使用示例

4. **開發文檔**
   - 更新 CLAUDE.md 或 CONTRIBUTING.md
   - 記錄架構決策

### 文檔風格

- 使用清晰、簡潔的語言
- 提供代碼示例
- 使用標準 Markdown 格式
- 文檔中可以適當使用 Emoji 增加可讀性

---

## 問題報告

### 報告 Bug

創建 Issue 時請包含：

1. **Bug 描述**
   - 預期行為
   - 實際行為
   - 重現步驟

2. **環境信息**
   - Python 版本
   - 操作系統
   - 相關依賴版本

3. **錯誤信息**
   - 完整的錯誤堆棧
   - 相關日誌

4. **重現步驟**
   - 最小化的重現示例
   - 測試數據

### Issue 模板

```markdown
## Bug 描述

簡要描述遇到的問題

## 重現步驟

1. 執行操作 A
2. 輸入數據 B
3. 點擊按鈕 C
4. 觀察到錯誤

## 預期行為

應該發生什麼

## 實際行為

實際發生了什麼

## 環境

- Python 版本: 3.9.7
- 操作系統: Windows 10
- Flask 版本: 3.0.0
- OpenAI 版本: 1.6.1

## 錯誤信息

```
粘貼完整的錯誤堆棧
```

## 額外信息

任何其他相關信息
```

### 功能請求

創建功能請求 Issue 時請包含：

1. 功能描述
2. 使用場景
3. 預期效果
4. 可能的實現方案

---

## 代碼審查

### 審查重點

作為審查者，請檢查：

- [ ] 代碼符合項目規範（特別是無 Emoji）
- [ ] 功能實現正確
- [ ] 測試覆蓋充分
- [ ] 文檔更新完整
- [ ] 無安全隱患
- [ ] 性能合理
- [ ] 錯誤處理完善

### 審查建議

- 提出建設性意見
- 說明原因和替代方案
- 保持友好和尊重

---

## 開發工具

### 推薦的 IDE 設置

#### VS Code

安裝擴展：

- Python
- Pylance
- Black Formatter
- autoDocstring

設置（.vscode/settings.json）：

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.pylintEnabled": false,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

- 配置 Black 為代碼格式化工具
- 啟用 PEP 8 檢查
- 配置 pytest 為測試運行器

### 開發輔助腳本

創建 `scripts/` 目錄存放開發腳本：

```bash
scripts/
├── format.sh       # 格式化代碼
├── lint.sh         # 代碼檢查
├── test.sh         # 運行測試
└── setup_dev.sh    # 開發環境設置
```

---

## 發布流程

### 版本號規則

遵循語義化版本（SemVer）：

- `MAJOR.MINOR.PATCH`
- MAJOR: 不兼容的 API 更改
- MINOR: 向後兼容的功能新增
- PATCH: 向後兼容的問題修正

### 發布步驟

1. 更新版本號
2. 更新 CHANGELOG.md
3. 創建 Git tag
4. 推送到遠程
5. 創建 GitHub Release

---

## 社區準則

### 行為準則

- 尊重所有貢獻者
- 接受建設性批評
- 關注項目最佳利益
- 展現同理心

### 溝通渠道

- GitHub Issues: 問題報告和功能請求
- Pull Requests: 代碼審查和討論
- Discussions: 一般性討論

---

## 獲取幫助

如有問題，請：

1. 查看現有文檔
2. 搜索已有 Issues
3. 創建新 Issue 提問

---

## 致謝

感謝所有為項目做出貢獻的開發者！

您的每一個 commit、Issue 和 Pull Request 都讓這個項目變得更好。

---

**再次強調**: 請務必閱讀 [CLAUDE.md](CLAUDE.md) 了解代碼規範，特別是關於不在代碼中使用 Emoji 的規定！
