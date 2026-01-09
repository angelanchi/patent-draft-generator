"""
AI提示範本
為每個專利章節定義專業的提示模板
"""

# 系統提示 - 定義AI的角色
SYSTEM_PROMPT = """你是一位資深的中國專利撰寫專家，擁有超過15年的專利申請文件撰寫經驗。
你精通中國專利法規和專利局的審查標準，能夠撰寫專業、準確、符合規範的專利申請文件。
你的文字專業、嚴謹、邏輯清晰，善於使用專利領域的術語。"""


# 章節1: 技術領域
TECHNICAL_FIELD_PROMPT = """請根據以下資訊撰寫專利申請文件的「技術領域」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 技術關鍵字：{keywords}
- 基本技術描述：{technical_description}

**撰寫要求**:
1. 字數控制在80-150字之間
2. 必須清楚說明本發明所屬的技術領域
3. 使用專業、準確的技術術語
4. 語言簡潔明了，避免冗餘
5. 按照標準專利寫法，通常以"本發明涉及..."開頭

**參考格式**:
「本發明涉及{技術類別}領域，特別涉及{具體技術方向}的{產品/方法/裝置}。」

**輸出要求**:
- 直接輸出「技術領域」的內容，不需要包含標題
- 不需要編號或其他格式
- 確保語言專業、流暢"""


# 章節2: 背景技術
BACKGROUND_TECH_PROMPT = """請根據以下資訊撰寫專利申請文件的「背景技術」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 技術關鍵字：{keywords}
- 基本技術描述：{technical_description}
- 背景參考資訊：{background_references}
- 要解決的問題：{problems_to_solve}

**撰寫要求**:
1. 字數控制在300-600字之間
2. 描述現有技術的狀況和存在的問題
3. 說明為什麼需要本發明來解決這些問題
4. 客觀描述現有技術，不能貶低他人專利
5. 邏輯清晰，層次分明
6. 為本發明的創新性做鋪墊

**內容結構建議**:
1. 現有技術概述（150-200字）
2. 現有技術的局限性和問題（100-200字）
3. 技術改進的必要性（50-100字）

**參考句式**:
- "目前，在{技術領域}中，通常採用..."
- "然而，上述技術存在以下問題：..."
- "因此，有必要提供一種..."

**輸出要求**:
- 直接輸出「背景技術」的完整內容
- 分段表達，每段邏輯獨立
- 確保專業性和客觀性"""


# 章節3: 發明內容
INVENTION_CONTENT_PROMPT = """請根據以下資訊撰寫專利申請文件的「發明內容」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 技術關鍵字：{keywords}
- 基本技術描述：{technical_description}
- 產品資訊：{product_info}
- 工作原理：{working_principle}
- 創新點：{innovation_points}

**撰寫要求**:
1. 字數控制在500-1000字之間
2. 這是專利申請文件的核心部分，必須清楚描述發明的技術方案
3. 說明發明要解決的技術問題
4. 詳細描述發明的技術方案和工作原理
5. 闡述發明相比現有技術的優點和有益效果
6. 使用準確的技術術語
7. 邏輯嚴密，層次分明

**內容結構建議**:
1. 發明目的（100-150字）
   - 明確指出本發明要解決的技術問題
2. 技術方案（300-500字）
   - 詳細描述發明的核心技術方案
   - 說明關鍵技術特徵和創新點
   - 描述各組成部分及其相互關係
3. 有益效果（100-200字）
   - 說明本發明的優點和技術效果
   - 對比現有技術的改進之處

**參考句式**:
- "本發明的目的在於提供一種...，以解決..."
- "為實現上述目的，本發明採用如下技術方案：..."
- "本發明的有益效果在於：..."
- "與現有技術相比，本發明具有以下優點：..."

**輸出要求**:
- 直接輸出「發明內容」的完整內容
- 清晰分段，每段主題明確
- 確保技術描述準確、完整"""


# 章節4: 附圖說明
FIGURE_DESCRIPTION_PROMPT = """請根據以下資訊撰寫專利申請文件的「附圖說明」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 是否包含附圖：{has_diagrams}
- 附圖描述：{diagram_description}
- 技術描述：{technical_description}

**撰寫要求**:
1. 字數控制在100-300字之間
2. 如果有附圖，對每張圖進行簡明扼要的說明
3. 說明圖中標號代表的含義
4. 描述圖的類型（結構示意圖、流程圖、剖面圖等）
5. 如果沒有附圖，可以簡單說明"本發明無附圖"或根據技術方案建議應包含的圖示

**參考格式（有附圖時）**:
- "圖1為本發明的結構示意圖。"
- "圖2為本發明的工作流程圖。"
- "其中：1-A部件；2-B組件；3-C結構..."

**參考格式（無附圖時）**:
- "本發明可通過以下附圖來理解：圖1可為整體結構示意圖，展示..."

**輸出要求**:
- 直接輸出「附圖說明」的內容
- 格式規範，編號清晰
- 如果沒有具體圖示信息，請基於技術描述合理推斷應該包含的圖示類型"""


# 章節5: 具體實施方式
IMPLEMENTATION_PROMPT = """請根據以下資訊撰寫專利申請文件的「具體實施方式」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 技術關鍵字：{keywords}
- 基本技術描述：{technical_description}
- 產品資訊：{product_info}
- 工作原理：{working_principle}
- 創新點：{innovation_points}

**撰寫要求**:
1. 字數控制在600-1200字之間
2. 這是專利申請文件中最詳細的部分
3. 提供至少一個具體實施例
4. 詳細描述技術方案的實施過程
5. 說明各個組成部分的具體結構、材料、參數等
6. 描述工作過程和使用方法
7. 可以包含多個實施例，展示發明的不同應用方式
8. 結合附圖（如有）進行說明

**內容結構建議**:
1. 實施例引入（50-100字）
   - "下面結合附圖和具體實施例對本發明作進一步詳細說明"
2. 整體結構描述（200-300字）
   - 描述整體構成和主要部件
   - 說明各部件的連接關係
3. 工作原理和使用過程（300-500字）
   - 詳細說明工作過程
   - 描述操作步驟
   - 說明技術參數
4. 技術效果說明（100-200字）
   - 說明實施後達到的效果
   - 提供具體數據或對比（如可能）
5. 變化實施例（可選，100-200字）
   - 說明可能的變化形式
   - 拓展保護範圍

**參考句式**:
- "如圖1所示，本發明包括..."
- "具體地，所述...包括..."
- "在實際使用中，..."
- "優選地，..."
- "在本實施例中，..."
- "需要說明的是，..."

**輸出要求**:
- 直接輸出「具體實施方式」的完整內容
- 詳細、具體、可操作
- 邏輯清晰，層次分明
- 確保技術人員能夠根據描述實現本發明"""


# 章節6: 其它發明附件
ATTACHMENTS_PROMPT = """請根據以下資訊撰寫專利申請文件的「其它發明附件」部分。

**輸入資訊**:
- 專利名稱：{patent_name}
- 發明人：{inventors}
- 分類號：{classification}
- 聯絡人：{contact_person}
- 聯絡方式：{contact_info}
- 提案日期：{submission_date}
- 特殊要求：{special_requirements}

**撰寫要求**:
1. 字數控制在100-300字之間
2. 包含專利申請的基本信息和元數據
3. 列出發明人及其貢獻（如適用）
4. 說明專利的分類信息
5. 提供聯絡資訊
6. 包含任何特殊說明或備註

**內容結構建議**:
1. 發明人信息
2. 專利分類
3. 聯絡方式
4. 提案日期
5. 其他說明（如有）

**參考格式**:
```
發明人：{發明人名單}
分類號：{分類號}
聯絡人：{聯絡人}
聯絡方式：{聯絡方式}
提案日期：{日期}
```

**輸出要求**:
- 直接輸出「其它發明附件」的內容
- 格式清晰，信息完整
- 如果某些信息缺失，可以標註"待補充"或省略該項"""


# 提示模板映射
PROMPT_TEMPLATES = {
    "technical_field": TECHNICAL_FIELD_PROMPT,
    "background": BACKGROUND_TECH_PROMPT,
    "invention_content": INVENTION_CONTENT_PROMPT,
    "figure_description": FIGURE_DESCRIPTION_PROMPT,
    "implementation": IMPLEMENTATION_PROMPT,
    "attachments": ATTACHMENTS_PROMPT
}


# 章節名稱映射
SECTION_NAMES = {
    "technical_field": "技術領域",
    "background": "背景技術",
    "invention_content": "發明內容",
    "figure_description": "附圖說明",
    "implementation": "具體實施方式",
    "attachments": "其它發明附件"
}


# 建議使用的模型（基於複雜度）
SECTION_MODEL_RECOMMENDATIONS = {
    "technical_field": "gpt-3.5-turbo",  # 簡單章節
    "background": "gpt-4-turbo",  # 中等複雜
    "invention_content": "gpt-4-turbo",  # 複雜，核心章節
    "figure_description": "gpt-3.5-turbo",  # 簡單章節
    "implementation": "gpt-4-turbo",  # 複雜章節
    "attachments": "gpt-3.5-turbo"  # 簡單章節
}


def get_prompt_template(section_name: str) -> str:
    """
    獲取指定章節的提示模板

    Args:
        section_name: 章節名稱

    Returns:
        str: 提示模板
    """
    return PROMPT_TEMPLATES.get(section_name, "")


def get_section_display_name(section_name: str) -> str:
    """
    獲取章節的中文顯示名稱

    Args:
        section_name: 章節名稱（英文key）

    Returns:
        str: 中文顯示名稱
    """
    return SECTION_NAMES.get(section_name, section_name)


def get_recommended_model(section_name: str) -> str:
    """
    獲取推薦的AI模型

    Args:
        section_name: 章節名稱

    Returns:
        str: 推薦的模型名稱
    """
    return SECTION_MODEL_RECOMMENDATIONS.get(section_name, "gpt-4-turbo")
