// 智能尽调分析系统 - 前端逻辑

// 切换tab功能
function switchTab(tab) {
    if (tab === 'query') {
        // 当前就是查询页面，不需要操作
    }
}

// 显示开发中弹窗
function showComingSoon(featureName) {
    const modal = document.getElementById('comingSoonModal');
    const modalText = document.getElementById('modalText');
    modalText.textContent = `${featureName}功能正在开发中，敬请期待！`;
    modal.style.display = 'flex';
}

// 关闭弹窗
function closeModal() {
    const modal = document.getElementById('comingSoonModal');
    modal.style.display = 'none';
}

// 点击弹窗外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('comingSoonModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

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

        // 风险评分进度条
        const riskScore = data.risk_analysis.risk_score || 50;
        const riskScoreValue = document.getElementById('riskScoreValue');
        const riskScoreFill = document.getElementById('riskScoreFill');

        riskScoreValue.textContent = riskScore + '分';
        riskScoreFill.style.width = riskScore + '%';
        riskScoreFill.className = 'risk-score-fill ' + riskLevel;

        // 如果有LLM分析结果，显示AI分析标识
        if (data.risk_analysis.llm_analysis) {
            // 检查是否已存在AI标识，避免重复添加
            let aiBadge = document.getElementById('aiAnalysisBadge');
            if (!aiBadge) {
                // 在报告卡片开头添加AI分析标识
                const resultCard = document.getElementById('reportCard');
                const aiBadgeHtml = `
                    <div id="aiAnalysisBadge" class="ai-badge">
                        <span class="ai-badge-icon">🤖</span>
                        <span>AI智能分析 · 基于通义千问大模型</span>
                    </div>
                    <div class="analysis-source">
                        <div class="analysis-source-title">
                            <span>🧠</span>
                            <span>AI分析说明</span>
                        </div>
                        <div class="analysis-source-text">
                            本报告由AI大模型基于企业基本信息、财务数据、交易流水等多维度信息进行综合分析推理生成。包含6大风险维度的智能评估、红旗信号识别及后续建议。
                        </div>
                    </div>
                `;
                resultCard.insertAdjacentHTML('afterbegin', aiBadgeHtml);
            }
        }

        // 维度评分卡片
        const dimensionScoresEl = document.getElementById('dimensionScores');
        dimensionScoresEl.innerHTML = '';

        const dimensionNames = {
            'operation_stability': '经营稳定',
            'cash_flow': '资金流向',
            'industry_risk': '行业风险',
            'transaction_behavior': '交易行为',
            'aml_screening': '反洗钱',
            'overall': '综合风险'
        };

        const findings = data.risk_analysis.findings || [];
        const dimensions = findings.filter(f => f.type_key && dimensionNames[f.type_key]);

        if (dimensions.length > 0) {
            dimensions.forEach(dim => {
                const card = document.createElement('div');
                card.className = 'dimension-card ' + dim.level.toLowerCase();
                card.innerHTML = `
                    <div class="dimension-name">${dimensionNames[dim.type_key] || dim.type}</div>
                    <div class="dimension-score">${dim.score}</div>
                `;
                dimensionScoresEl.appendChild(card);
            });
        }

        // 红旗信号
        const redFlags = findings.filter(f => f.type_key === 'red_flags');
        const redFlagsSection = document.getElementById('redFlagsSection');
        const redFlagsList = document.getElementById('redFlagsList');

        if (redFlags.length > 0) {
            redFlagsSection.style.display = 'block';
            redFlagsList.innerHTML = '';
            redFlags.forEach(flag => {
                const div = document.createElement('div');
                div.className = 'red-flag';
                div.innerHTML = `
                    <span class="red-flag-icon">🚩</span>
                    <span class="red-flag-text">${flag.detail}</span>
                `;
                redFlagsList.appendChild(div);
            });
        } else {
            redFlagsSection.style.display = 'none';
        }

        // 关键发现
        const findingsList = document.getElementById('findingsList');
        findingsList.innerHTML = '';

        const keyFindings = findings.filter(f => f.type_key === 'key_findings' || !f.type_key);
        keyFindings.forEach(finding => {
            const li = document.createElement('li');
            li.className = finding.level ? finding.level.toLowerCase() : 'medium';
            li.textContent = `${finding.type || '发现'}：${finding.detail || finding.finding}`;
            findingsList.appendChild(li);
        });

        // 建议
        const recommendations = data.risk_analysis.recommendations || [];
        const suggestionText = document.getElementById('suggestionText');

        if (recommendations.length > 0) {
            suggestionText.innerHTML = recommendations.map(r => `• ${r}`).join('<br>');
        } else {
            suggestionText.textContent = data.summary?.recommendation || '建议持续监控';
        }

        // 后续步骤
        const nextSteps = data.risk_analysis.next_steps || [];
        const nextStepsSection = document.getElementById('nextStepsSection');
        const nextStepsList = document.getElementById('nextStepsList');

        if (nextSteps.length > 0) {
            nextStepsSection.style.display = 'block';
            nextStepsList.innerHTML = '';
            nextSteps.forEach(step => {
                const li = document.createElement('li');
                li.style.padding = '8px 0';
                li.style.borderBottom = '1px solid #f0f0f0';
                li.style.fontSize = '13px';
                li.style.color = '#555';
                li.textContent = '• ' + step;
                nextStepsList.appendChild(li);
            });
        } else {
            nextStepsSection.style.display = 'none';
        }

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
