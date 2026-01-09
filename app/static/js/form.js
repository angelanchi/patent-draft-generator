/**
 * 多步驟表單處理
 */

let currentStep = 1;
const totalSteps = 4;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initForm();
    setupEventListeners();
    showStep(1);
});

// 初始化表單
function initForm() {
    // 設置今天的日期為默認值
    const dateInput = document.getElementById('submission_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    // 附圖勾選框處理
    const hasDiagramsCheckbox = document.getElementById('has_diagrams');
    const diagramGroup = document.getElementById('diagram_group');

    if (hasDiagramsCheckbox && diagramGroup) {
        hasDiagramsCheckbox.addEventListener('change', (e) => {
            diagramGroup.style.display = e.target.checked ? 'block' : 'none';
        });
    }
}

// 設置事件監聽器
function setupEventListeners() {
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('patentForm');

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                nextStep();
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', prevStep);
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', submitForm);
    }

    // Enter鍵處理
    form.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            if (currentStep < totalSteps) {
                nextBtn.click();
            } else {
                submitBtn.click();
            }
        }
    });
}

// 顯示指定步驟
function showStep(step) {
    // 更新當前步驟
    currentStep = step;

    // 隱藏所有步驟
    document.querySelectorAll('.form-step').forEach(el => {
        el.classList.remove('active');
    });

    // 顯示當前步驟
    const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    if (currentStepEl) {
        currentStepEl.classList.add('active');
    }

    // 更新進度指示器
    updateProgressIndicator(step);

    // 更新按鈕顯示
    updateButtons(step);

    // 如果是最後一步，顯示摘要和估算成本
    if (step === totalSteps) {
        showSummary();
        estimateCost();
    }

    // 滾動到頂部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 更新進度指示器
function updateProgressIndicator(step) {
    document.querySelectorAll('.step').forEach((el, index) => {
        const stepNum = index + 1;
        el.classList.remove('active', 'completed');

        if (stepNum < step) {
            el.classList.add('completed');
        } else if (stepNum === step) {
            el.classList.add('active');
        }
    });
}

// 更新按鈕
function updateButtons(step) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');

    // 上一步按鈕
    prevBtn.style.display = step > 1 ? 'inline-block' : 'none';

    // 下一步按鈕
    nextBtn.style.display = step < totalSteps ? 'inline-block' : 'none';

    // 提交按鈕
    submitBtn.style.display = step === totalSteps ? 'inline-block' : 'none';
}

// 驗證當前步驟
function validateStep(step) {
    const currentStepEl = document.querySelector(`.form-step[data-step="${step}"]`);
    const requiredInputs = currentStepEl.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#f44336';

            // 2秒後恢復邊框顏色
            setTimeout(() => {
                input.style.borderColor = '';
            }, 2000);
        }
    });

    if (!isValid) {
        Utils.showNotification('請填寫所有必填欄位', 'error');
    }

    return isValid;
}

// 下一步
function nextStep() {
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

// 上一步
function prevStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

// 顯示摘要
function showSummary() {
    const formData = getFormData();
    const summaryContainer = document.getElementById('summary-content');

    const summaryHTML = `
        <div class="summary-item">
            <strong>專利名稱：</strong>
            <span>${formData.patent_name || '-'}</span>
        </div>
        <div class="summary-item">
            <strong>發明人：</strong>
            <span>${formData.inventors || '-'}</span>
        </div>
        <div class="summary-item">
            <strong>技術關鍵字：</strong>
            <span>${formData.keywords || '-'}</span>
        </div>
        <div class="summary-item">
            <strong>技術描述：</strong>
            <span>${truncateText(formData.technical_description, 200)}</span>
        </div>
    `;

    summaryContainer.innerHTML = summaryHTML;
}

// 估算成本
async function estimateCost() {
    const costInfo = document.getElementById('cost-info');

    try {
        const formData = getFormData();

        const result = await Utils.apiRequest('/api/estimate/cost', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        if (result.success) {
            const cost = result.cost_estimate;
            costInfo.innerHTML = `
                <p><strong>預估總成本：</strong> $${cost.total_cost.toFixed(4)} USD</p>
                <p class="text-muted">實際成本可能略有不同，取決於內容長度</p>
            `;
        } else {
            costInfo.innerHTML = `<p class="text-muted">無法估算成本</p>`;
        }
    } catch (error) {
        costInfo.innerHTML = `<p class="text-muted">成本估算失敗</p>`;
    }
}

// 獲取表單數據
function getFormData() {
    const form = document.getElementById('patentForm');
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }

    // 處理勾選框
    data.has_diagrams = document.getElementById('has_diagrams').checked;

    return data;
}

// 提交表單
async function submitForm() {
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.textContent;

    // 禁用按鈕
    submitBtn.disabled = true;
    submitBtn.textContent = '正在提交...';

    try {
        const formData = getFormData();

        // 保存表單數據到sessionStorage
        sessionStorage.setItem('patentFormData', JSON.stringify(formData));

        // 跳轉到生成頁面
        window.location.href = '/generating';

    } catch (error) {
        console.error('提交失敗:', error);
        Utils.showNotification('提交失敗: ' + error.message, 'error');

        // 恢復按鈕
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// 截斷文字
function truncateText(text, maxLength) {
    if (!text) return '-';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 添加摘要項目樣式
const style = document.createElement('style');
style.textContent = `
    .summary-item {
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        gap: 10px;
    }

    .summary-item:last-child {
        border-bottom: none;
    }

    .summary-item strong {
        min-width: 120px;
        color: #667eea;
    }

    .summary-item span {
        flex: 1;
        color: #333;
    }
`;
document.head.appendChild(style);
