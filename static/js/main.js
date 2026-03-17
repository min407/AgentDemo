// 银行智能尽调Agent - 前端逻辑

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const keywordInput = document.getElementById('keywordInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultSection = document.getElementById('resultSection');
    const exportBtn = document.getElementById('exportBtn');

    // 默认值
    const defaultValue = '深圳市赛为智能股份有限公司';

    // 初始状态：显示默认值，灰色
    keywordInput.value = defaultValue;
    keywordInput.style.color = '#bbb';

    // 输入框焦点事件
    keywordInput.addEventListener('focus', function() {
        if (this.value === defaultValue) {
            this.value = '';
            this.style.color = '#333';
        }
    });

    // 输入框失焦事件
    keywordInput.addEventListener('blur', function() {
        if (!this.value.trim()) {
            this.value = defaultValue;
            this.style.color = '#bbb';
        }
    });

    // 绑定事件
    analyzeBtn.addEventListener('click', startAnalysis);
    keywordInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            startAnalysis();
        }
    });
    exportBtn.addEventListener('click', exportReport);

    // 开始分析
    async function startAnalysis() {
        let keyword = keywordInput.value.trim();
        // 如果为空，使用默认值
        if (!keyword) {
            keyword = defaultValue;
            keywordInput.value = defaultValue;
            keywordInput.style.color = '#bbb';
        }

        // 禁用按钮
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading"></span> 分析中...';

        // 重置状态
        resetSteps();
        resultSection.style.display = 'none';

        try {
            // 调用API
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ keyword })
            });

            const result = await response.json();

            if (result.success) {
                // 显示步骤进度
                await showSteps(result.steps);
                // 显示结果
                showResult(result.result);
            } else {
                alert(result.error || '分析失败');
            }

        } catch (error) {
            console.error('Error:', error);
            alert('请求失败，请重试');
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = '开始分析';
        }
    }

    // 重置步骤状态
    function resetSteps() {
        for (let i = 1; i <= 4; i++) {
            const step = document.getElementById('step' + i);
            step.classList.remove('active', 'completed');
            step.querySelector('.step-num').textContent = i;
        }
    }

    // 显示步骤进度
    async function showSteps(steps) {
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            const stepNum = i + 1;

            // 激活步骤
            const stepEl = document.getElementById('step' + stepNum);
            if (stepEl) {
                stepEl.classList.add('active');
                stepEl.classList.add('completed');
                // 显示完成勾选
                stepEl.querySelector('.step-num').textContent = '✓';
            }

            // 模拟延迟
            await sleep(600);
        }
    }

    // 显示分析结果
    function showResult(result) {
        const data = result;

        // 隐藏进度区域
        document.getElementById('progressSection').style.display = 'none';

        // 企业信息
        const enterprise = data.enterprise;
        document.getElementById('companyName').textContent = enterprise.customer_name;
        document.getElementById('industry').textContent = enterprise.industry;
        document.getElementById('regCapital').textContent = formatAmount(enterprise.reg_capital);

        // 风险等级
        const riskLevel = data.risk_analysis.risk_level;
        const riskBadge = document.getElementById('riskBadge');
        const riskText = document.getElementById('riskText');
        const riskLevelEl = document.getElementById('riskLevel');

        riskBadge.className = 'risk-badge ' + riskLevel;
        riskText.textContent = getRiskText(riskLevel);
        riskLevelEl.textContent = getRiskText(riskLevel);

        // 关键发现
        const findingsList = document.getElementById('findingsList');
        findingsList.innerHTML = '';

        const findings = data.risk_analysis.findings || [];
        findings.forEach(finding => {
            const li = document.createElement('li');
            li.className = finding.level.toLowerCase();
            li.textContent = `${finding.type}：${finding.detail}`;
            findingsList.appendChild(li);
        });

        // 建议
        const recommendation = data.summary.recommendation;
        document.getElementById('suggestionText').textContent = recommendation;

        // 显示结果区域
        resultSection.style.display = 'block';

        // 滚动到结果
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // 格式化金额
    function formatAmount(amount) {
        if (amount >= 10000) {
            return (amount / 10000).toFixed(0) + '万';
        }
        return amount + '元';
    }

    // 获取风险等级文本
    function getRiskText(level) {
        const map = {
            'high': '高风险',
            'medium': '中等风险',
            'low': '低风险'
        };
        return map[level] || '未知';
    }

    // 导出报告
    function exportReport() {
        const resultCard = document.querySelector('.result-card');
        if (!resultCard) {
            alert('请先生成分析报告');
            return;
        }

        const companyName = document.getElementById('companyName').textContent || '企业尽调报告';
        const riskLevel = document.getElementById('riskText').textContent || '风险报告';

        // PDF导出配置
        const opt = {
            margin: 10,
            filename: `${companyName}_尽调报告_${new Date().toISOString().slice(0,10)}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        // 使用html2pdf导出
        html2pdf().set(opt).from(resultCard).save();
    }

    // 休眠函数
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
});
