"""
專利生成測試腳本
用於測試完整的專利文件生成流程
"""
import requests
import json
from datetime import datetime

# API配置
API_BASE_URL = "http://127.0.0.1:5000/api"

# 測試數據 - 虛構示範案例（非真實專利提案）
TEST_PATENT_DATA = {
    "patent_name": "一種具土壤濕度感測之盆栽自動澆水裝置及方法",
    "inventors": "王小明、林小華",
    "classification": "A01G",
    "contact_person": "王小明",
    "contact_number": "0000",
    "contact_email": "demo@example.com",
    "submission_date": "2025-03-08",

    "keywords": "自動澆水, 土壤濕度感測, 盆栽, 微控制器, smart irrigation",

    "technical_description": """
    本發明涉及園藝自動化技術領域，特別是一種依據土壤濕度自動決定澆水時機與水量的
    盆栽澆水裝置及方法。傳統定時澆水無法反映植物實際需水量，容易過度或不足澆水。
    本發明以電容式土壤濕度感測器即時量測含水率，由微控制器比較設定門檻後驅動微型
    水泵，並記錄每次澆水量，達到依需求精準供水的效果。
    """,

    "product_info": """
    裝置包括：電容式土壤濕度感測器、微控制器、微型水泵、儲水槽水位感測器、
    以及無線模組。濕度門檻可依植物種類設定，儲水不足時發出提醒。
    """,

    "working_principle": """
    微控制器每 10 分鐘讀取一次土壤濕度。濕度低於門檻時啟動水泵，
    並在濕度回升到目標值或達到單次最大水量時停止。系統記錄每次澆水的時間與水量，
    供使用者調整門檻。
    """,

    "innovation_points": """
    1. 依實際需求澆水：避免定時澆水造成的過度或不足
    2. 節省用水：單次水量有上限，並可依紀錄調整
    3. 低維護：儲水不足時主動提醒
    """,

    "background_references": """
    現有盆栽澆水多採定時器控制，只依時間不依土壤狀態，
    在天氣與季節變化時無法調整，且缺乏用水紀錄。
    """,

    "problems_to_solve": """
    解決定時澆水無法反映植物實際需水量、浪費用水且缺乏紀錄的問題。
    """,

    "has_diagrams": True,
    "diagram_description": """
    圖1為本發明裝置的整體結構示意圖；
    圖2為控制流程圖。
    """,

    "special_requirements": """
    請強調依感測值決定澆水的控制邏輯，並清楚描述門檻設定方式。
    """
}


def test_api_health():
    """測試API健康狀態"""
    print("\n" + "="*60)
    print("1. 測試API健康狀態")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE_URL}/test")
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False


def test_input_validation():
    """測試輸入驗證"""
    print("\n" + "="*60)
    print("2. 測試輸入數據驗證")
    print("="*60)

    try:
        response = requests.post(
            f"{API_BASE_URL}/validate/input",
            json=TEST_PATENT_DATA,
            headers={'Content-Type': 'application/json'}
        )
        print(f"狀態碼: {response.status_code}")
        result = response.json()
        print(f"驗證結果: {'✅ 通過' if result.get('success') else '❌ 失敗'}")
        if not result.get('success'):
            print(f"錯誤: {result.get('errors')}")
        return result.get('success', False)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False


def test_cost_estimation():
    """測試成本估算"""
    print("\n" + "="*60)
    print("3. 測試生成成本估算")
    print("="*60)

    try:
        response = requests.post(
            f"{API_BASE_URL}/estimate/cost",
            json=TEST_PATENT_DATA,
            headers={'Content-Type': 'application/json'}
        )
        print(f"狀態碼: {response.status_code}")
        result = response.json()

        if result.get('success'):
            cost = result.get('cost_estimate', {})
            print(f"✅ 估算成功")
            print(f"總成本: ${cost.get('total_cost', 0):.4f} USD")
            print(f"幣種: {cost.get('currency', 'USD')}")
        else:
            print(f"❌ 估算失敗: {result.get('error')}")

        return result.get('success', False)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False


def test_section_generation():
    """測試單個章節生成"""
    print("\n" + "="*60)
    print("4. 測試單個章節生成（技術領域）")
    print("="*60)

    test_data = {
        "section_name": "technical_field",
        "patent_data": {
            "patent_name": TEST_PATENT_DATA["patent_name"],
            "keywords": TEST_PATENT_DATA["keywords"],
            "technical_description": TEST_PATENT_DATA["technical_description"]
        }
    }

    try:
        print("正在調用OpenAI API生成內容...")
        response = requests.post(
            f"{API_BASE_URL}/generate/section",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        print(f"狀態碼: {response.status_code}")
        result = response.json()

        if result.get('success'):
            print(f"✅ 生成成功")
            print(f"章節: {result.get('section_name')}")
            print(f"字數: {result.get('word_count')}")
            print(f"\n生成內容:\n{'-'*60}")
            print(result.get('content'))
            print('-'*60)
        else:
            print(f"❌ 生成失敗: {result.get('error')}")

        return result.get('success', False)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False


def test_full_patent_generation():
    """測試完整專利生成"""
    print("\n" + "="*60)
    print("5. 測試完整專利文件生成")
    print("="*60)
    print("⚠️  這將調用OpenAI API生成完整的6個章節")
    print("⚠️  預計耗時: 2-5分鐘")
    print("⚠️  預估成本: $0.10-0.20 USD")

    confirm = input("\n是否繼續? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消測試")
        return False

    try:
        print("\n開始生成專利文件...")
        print("請耐心等待，這可能需要幾分鐘...")

        start_time = datetime.now()

        response = requests.post(
            f"{API_BASE_URL}/generate/patent",
            json=TEST_PATENT_DATA,
            headers={'Content-Type': 'application/json'},
            timeout=600  # 10分鐘超時
        )

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        print(f"\n狀態碼: {response.status_code}")
        result = response.json()

        if result.get('success'):
            print(f"\n✅ 專利文件生成成功！")
            print(f"\n生成信息:")
            print(f"  - 耗時: {elapsed_time:.2f} 秒")
            print(f"  - 文件路徑: {result.get('file_path')}")

            patent_info = result.get('patent_info', {})
            print(f"\n專利信息:")
            print(f"  - 專利ID: {patent_info.get('patent_id')}")
            print(f"  - 專利名稱: {patent_info.get('patent_name')}")
            print(f"  - 總字數: {patent_info.get('total_word_count')}")
            print(f"  - 生成時間: {patent_info.get('generated_at')}")

            print(f"\n📄 Word文檔已生成，請在 output/ 目錄中查看")

        else:
            print(f"\n❌ 生成失敗")
            print(f"錯誤: {result.get('error')}")
            print(f"詳情: {result.get('message', '')}")

        return result.get('success', False)

    except requests.Timeout:
        print(f"\n❌ 請求超時（超過10分鐘）")
        return False
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        return False


def main():
    """主測試函數"""
    print("\n" + "="*60)
    print("AI 專利文件生成器 - 測試腳本")
    print("="*60)
    print(f"API地址: {API_BASE_URL}")
    print(f"測試專利: {TEST_PATENT_DATA['patent_name']}")

    print("\n⚠️  注意事項:")
    print("1. 請確保已啟動Flask應用: python run.py")
    print("2. 請確保已在.env文件中配置OpenAI API密鑰")
    print("3. 完整測試會調用OpenAI API，會產生費用（約$0.10-0.20）")

    print("\n" + "="*60)
    print("開始測試...")
    print("="*60)

    results = {}

    # 測試1: API健康檢查
    results['health'] = test_api_health()

    if not results['health']:
        print("\n❌ API未運行，請先啟動Flask應用")
        print("運行命令: python run.py")
        return

    # 測試2: 輸入驗證
    results['validation'] = test_input_validation()

    # 測試3: 成本估算
    results['cost'] = test_cost_estimation()

    # 測試4: 單個章節生成（需要API密鑰）
    print("\n" + "="*60)
    test_section = input("是否測試單個章節生成? (需要OpenAI API密鑰) (y/n): ")
    if test_section.lower() == 'y':
        results['section'] = test_section_generation()

    # 測試5: 完整專利生成（需要API密鑰且會產生費用）
    print("\n" + "="*60)
    test_full = input("是否測試完整專利生成? (需要OpenAI API密鑰，會產生費用) (y/n): ")
    if test_full.lower() == 'y':
        results['full_patent'] = test_full_patent_generation()

    # 測試總結
    print("\n" + "="*60)
    print("測試總結")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{test_name.ljust(20)}: {status}")

    print("\n測試完成！")


if __name__ == "__main__":
    main()
