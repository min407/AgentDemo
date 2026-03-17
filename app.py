"""
银行智能尽调Agent - Flask Web服务
"""
import json
import re
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# 导入LLM模块
from llm_client import get_client
from config import QWEN_MODEL

app = Flask(__name__)
CORS(app)

# 初始化LLM客户端
llm_client = get_client(use_mock=False)

# ==================== 模拟数据 ====================
MOCK_ENTERPRISES = {
    "深圳市恒盈投资集团有限公司": {
        "credit_code": "91440300MA5G7P4L4X",
        "customer_no": "C20240001",
        "customer_name": "深圳市恒盈投资集团有限公司",
        "legal_person": "邓海强",
        "reg_capital": 50000000,
        "establish_date": "2020-06-03",
        "industry": "金融业-资本市场服务",
        "address": "深圳市南山区粤海街道科技园社区科苑路8号讯美科技广场2号楼1501",
        "business_scope": "投资兴办实业；投资咨询；创业项目投资；以自有资金从事投资活动",
        "employees": 0,
        "risk_level": "low",
        "enterprise_type": "有限责任公司",
        "company_size": "XS（微型）"
    },
    "深圳市赛为智能股份有限公司": {
        "credit_code": "91440300279316343L",
        "customer_no": "C20240002",
        "customer_name": "深圳市赛为智能股份有限公司",
        "legal_person": "周起如",
        "reg_capital": 763869228,
        "establish_date": "1997-02-27",
        "industry": "信息技术-计算机-IT服务",
        "address": "深圳市龙岗区南湾街道下李朗社区联李东路8号赛为大楼A101至15楼",
        "business_scope": "人工智能系统、无人机研发、销售；计算机软件产品开发、销售；智慧城市项目投资",
        "employees": 61,
        "risk_level": "medium",
        "enterprise_type": "上市股份有限公司",
        "company_size": "M（中型）",
        "stock_code": "300044"
    },
    "深圳市长亮科技股份有限公司": {
        "credit_code": "91440300736295868L",
        "customer_no": "C20240003",
        "customer_name": "深圳市长亮科技股份有限公司",
        "legal_person": "王长春",
        "reg_capital": 812253787,
        "establish_date": "2002-04-28",
        "industry": "信息技术-计算机-软件开发",
        "address": "深圳市南山区粤海街道沙河西路深圳湾科技生态园一区2栋A座5层",
        "business_scope": "计算机软硬件开发及服务；金融科技解决方案；数字人民币系统",
        "employees": 578,
        "risk_level": "low",
        "enterprise_type": "其他股份有限公司（上市）",
        "company_size": "L（大型）",
        "stock_code": "300348"
    },
    "滴滴出行科技有限公司": {
        "credit_code": "911201163409833307",
        "customer_no": "C20240004",
        "customer_name": "滴滴出行科技有限公司",
        "legal_person": "肖建",
        "reg_capital": 50000000,
        "establish_date": "2015-07-29",
        "industry": "信息技术-互联网服务-互联网平台",
        "address": "天津经济技术开发区第一大街79号泰达MSD-C区C2座21层2103室",
        "business_scope": "网络预约出租汽车客运经营；电信业务；软件开发",
        "employees": 4,
        "risk_level": "medium",
        "enterprise_type": "有限责任公司（法人独资）",
        "company_size": "XS（微型）"
    },
    "金蝶软件（中国）有限公司": {
        "credit_code": "914403006188392540",
        "customer_no": "C20240005",
        "customer_name": "金蝶软件（中国）有限公司",
        "legal_person": "章勇",
        "reg_capital": 1400000000,
        "establish_date": "1993-08-05",
        "industry": "信息技术-计算机-软件开发",
        "address": "深圳市南山区科技园科技南十二路2号金蝶软件园A座1-8层",
        "business_scope": "生产、开发、经营电脑软硬件；企业管理云服务；ERP系统",
        "employees": 3457,
        "risk_level": "low",
        "enterprise_type": "有限责任公司（外国法人独资）",
        "company_size": "L（大型）",
        "stock_code": "00268.HK"
    }
}

# 模拟交易数据
MOCK_TRANSACTIONS = {
    # 深圳市恒盈投资集团有限公司
    "C20240001": {
        "period": "2024-01 to 2024-03",
        "total_income": 15000000,
        "total_outflow": 12000000,
        "balance": 8000000,
        "avg_monthly_income": 5000000,
        "avg_monthly_expense": 4000000,
        "transaction_count": 35,
        "large_transactions": [
            {"date": "2024-02-15", "amount": 5000000, "type": "in", "desc": "投资收益"},
            {"date": "2024-03-10", "amount": 3000000, "type": "out", "desc": "项目投资"}
        ]
    },
    # 深圳市赛为智能股份有限公司
    "C20240002": {
        "period": "2024-01 to 2024-03",
        "total_income": 28000000,
        "total_outflow": 25000000,
        "balance": 15000000,
        "avg_monthly_income": 9333333,
        "avg_monthly_expense": 8333333,
        "transaction_count": 120,
        "large_transactions": [
            {"date": "2024-01-20", "amount": 8000000, "type": "in", "desc": "项目回款"},
            {"date": "2024-02-28", "amount": 5000000, "type": "out", "desc": "设备采购"},
            {"date": "2024-03-15", "amount": 3000000, "type": "out", "desc": "研发投入"}
        ]
    },
    # 深圳市长亮科技股份有限公司
    "C20240003": {
        "period": "2024-01 to 2024-03",
        "total_income": 45000000,
        "total_outflow": 38000000,
        "balance": 28000000,
        "avg_monthly_income": 15000000,
        "avg_monthly_expense": 12666667,
        "transaction_count": 180,
        "large_transactions": [
            {"date": "2024-01-10", "amount": 12000000, "type": "in", "desc": "合同收入"},
            {"date": "2024-02-20", "amount": 8000000, "type": "in", "desc": "项目收入"},
            {"date": "2024-03-05", "amount": 6000000, "type": "out", "desc": "人工成本"}
        ]
    },
    # 滴滴出行科技有限公司
    "C20240004": {
        "period": "2024-01 to 2024-03",
        "total_income": 8500000,
        "total_outflow": 8200000,
        "balance": 3500000,
        "avg_monthly_income": 2833333,
        "avg_monthly_expense": 2733333,
        "transaction_count": 45,
        "large_transactions": [
            {"date": "2024-02-10", "amount": 2000000, "type": "out", "desc": "平台补贴"},
            {"date": "2024-03-01", "amount": 1500000, "type": "in", "desc": "平台收入"}
        ]
    },
    # 金蝶软件（中国）有限公司
    "C20240005": {
        "period": "2024-01 to 2024-03",
        "total_income": 120000000,
        "total_outflow": 95000000,
        "balance": 65000000,
        "avg_monthly_income": 40000000,
        "avg_monthly_expense": 31666667,
        "transaction_count": 320,
        "large_transactions": [
            {"date": "2024-01-15", "amount": 35000000, "type": "in", "desc": "软件授权收入"},
            {"date": "2024-02-20", "amount": 20000000, "type": "in", "desc": "云服务收入"},
            {"date": "2024-03-10", "amount": 15000000, "type": "out", "desc": "研发投入"},
            {"date": "2024-03-25", "amount": 10000000, "type": "out", "desc": "人员成本"}
        ]
    }
}

# ==================== 工具函数 ====================

def query_enterprise(keyword: str):
    """查询企业信息"""
    # 精确匹配
    if keyword in MOCK_ENTERPRISES:
        return MOCK_ENTERPRISES[keyword]

    # 模糊匹配
    for name, info in MOCK_ENTERPRISES.items():
        if keyword in name or info.get("credit_code") == keyword or info.get("customer_no") == keyword:
            return info

    return None


def query_transactions(customer_no: str):
    """查询交易流水"""
    return MOCK_TRANSACTIONS.get(customer_no, {
        "period": "2024-01 to 2024-03",
        "total_income": 5000000,
        "total_outflow": 4800000,
        "balance": 2000000,
        "avg_monthly_income": 1660000,
        "avg_monthly_expense": 1600000,
        "transaction_count": 100,
        "large_transactions": []
    })


def analyze_risk(enterprise_info, transactions):
    """风险分析 - 接入LLM智能分析"""
    risk_findings = []

    # ========== LLM智能分析 ==========
    # 构建prompt - 优化后的更全面分析框架
    # 企业成立年限
    import datetime
    try:
        est_date = datetime.datetime.strptime(enterprise_info.get('establish_date', '2000-01-01'), '%Y-%m-%d')
        years_since_establish = (datetime.datetime.now() - est_date).days // 365
    except:
        years_since_establish = 0

    # 计算收入支出比
    income = transactions.get('total_income', 0)
    expense = transactions.get('total_outflow', 0)
    income_expense_ratio = (income - expense) / income * 100 if income > 0 else 0

    prompt = f"""你是一个资深的银行风险尽调分析师，擅长企业信用风险评估和反洗钱筛查。请根据以下企业信息进行专业、深入的风险评估。

## 一、企业基本信息
| 字段 | 内容 |
|------|------|
| 企业名称 | {enterprise_info.get('customer_name', '未知')} |
| 统一社会信用代码 | {enterprise_info.get('credit_code', '未知')} |
| 行业分类 | {enterprise_info.get('industry', '未知')} |
| 注册资本 | {enterprise_info.get('reg_capital', 0)}万元 |
| 成立日期 | {enterprise_info.get('establish_date', '未知')}（已成立{years_since_establish}年） |
| 法定代表人人 | {enterprise_info.get('legal_person', '未知')} |
| 企业规模 | {enterprise_info.get('company_size', '未知')} |
| 风险评级 | {enterprise_info.get('risk_level', '未知')} |
| 经营范围 | {enterprise_info.get('business_scope', '未知')} |

## 二、财务与交易数据
| 指标 | 数值 |
|------|------|
| 账户余额 | {_format_amount(transactions.get('balance', 0))} |
| 近3个月收入 | {_format_amount(transactions.get('total_income', 0))} |
| 近3个月支出 | {_format_amount(transactions.get('total_outflow', 0))} |
| 收支盈余率 | {income_expense_ratio:.1f}% |
| 交易笔数 | {transactions.get('transaction_count', 0)}笔 |
| 月均交易笔数 | {transactions.get('transaction_count', 0) // 3}笔/月 |

## 三、大额交易明细
{chr(10).join([f"- {tx['date']}: {'收入' if tx['type']=='in' else '支出'} {tx['amount']/10000:.0f}万 - {tx['desc']}" for tx in transactions.get('large_transactions', [])]) if transactions.get('large_transactions') else '无大额交易记录'}

## 四、分析框架与要求

请从以下**6个核心维度**进行深度分析：

### 1. 经营稳定性分析 (Operation Stability)
- 成立年限与注册资本是否匹配
- 经营周期是否稳定
- 收入支出是否健康

### 2. 资金流向分析 (Cash Flow Analysis)
- 资金流入来源是否分散
- 大额资金进出是否合理
- 是否存在异常资金归集

### 3. 行业风险评估 (Industry Risk)
- 所在行业周期阶段
- 行业政策影响（是否为监管重点行业）
- 行业竞争格局

### 4. 交易行为分析 (Transaction Behavior)
- 交易频率是否异常
- 是否存在夜间交易
- 是否有集中转入分散转出等可疑特征

### 5. 反洗钱筛查 (AML Screening)
- 是否涉及可疑交易特征
- 是否符合客户身份
- 是否需要加强型尽职调查

### 6. 综合风险评级 (Overall Risk Rating)
- 综合以上各维度，给出最终风险等级

## 五、输出要求

请返回以下JSON格式，必须包含所有字段：

{{
    "risk_level": "low/medium/high",
    "risk_score": 0-100,
    "dimensions": {{
        "operation_stability": {{"score": 0-100, "finding": "分析发现", "detail": "具体说明"}},
        "cash_flow": {{"score": 0-100, "finding": "分析发现", "detail": "具体说明"}},
        "industry_risk": {{"score": 0-100, "finding": "分析发现", "detail": "具体说明"}},
        "transaction_behavior": {{"score": 0-100, "finding": "分析发现", "detail": "具体说明"}},
        "aml_screening": {{"score": 0-100, "finding": "分析发现", "detail": "具体说明"}},
        "overall": {{"score": 0-100, "finding": "综合评估", "detail": "综合说明"}}
    }},
    "key_findings": ["关键发现1（带具体数据支撑）", "关键发现2", "关键发现3"],
    "red_flags": ["红旗信号1（如有）", "红旗信号2（如有）"],
    "recommendations": ["具体建议1", "具体建议2", "具体建议3"],
    "next_steps": ["后续行动1", "后续行动2"]
}}

注意：
1. 每个维度的score必须是0-100的整数
2. finding字段要用一句话精炼概括
3. detail字段要包含具体数据分析和逻辑支撑
4. 如果没有发现问题，score给低分并说明"未发现异常"
5. 只返回JSON，不要任何其他内容"""

    try:
        # 调用LLM
        llm_result = llm_client.call(prompt, system_prompt="你是一个专业的银行风险分析师，擅长企业信用风险评估。")

        # 解析LLM返回的JSON
        import json as json_module
        # 尝试提取JSON
        try:
            # 尝试直接解析
            llm_data = json_module.loads(llm_result)
        except:
            # 如果直接解析失败，尝试提取```json ```块
            import re
            json_match = re.search(r'\{[\s\S]*\}', llm_result)
            if json_match:
                llm_data = json_module.loads(json_match.group())
            else:
                llm_data = None

        if llm_data:
            # 转换LLM结果为统一格式 - 支持6个维度
            risk_findings = []
            dimension_names = {
                "operation_stability": "经营稳定性",
                "cash_flow": "资金流向",
                "industry_risk": "行业风险",
                "transaction_behavior": "交易行为",
                "aml_screening": "反洗钱筛查",
                "overall": "综合风险"
            }

            for key, value in llm_data.get("dimensions", {}).items():
                score = value.get("score", 0)
                if score >= 70:
                    level = "HIGH"
                elif score >= 40:
                    level = "MEDIUM"
                else:
                    level = "LOW"
                risk_findings.append({
                    "type": dimension_names.get(key, key),
                    "type_key": key,
                    "level": level,
                    "finding": value.get("finding", ""),
                    "detail": value.get("detail", ""),
                    "score": score
                })

            # 添加关键发现
            for finding in llm_data.get("key_findings", []):
                risk_findings.append({
                    "type": "关键发现",
                    "type_key": "key_findings",
                    "level": "MEDIUM",
                    "finding": finding,
                    "detail": finding,
                    "score": 50
                })

            # 添加红旗信号
            for flag in llm_data.get("red_flags", []):
                risk_findings.append({
                    "type": "红旗信号",
                    "type_key": "red_flags",
                    "level": "HIGH",
                    "finding": flag,
                    "detail": flag,
                    "score": 80
                })

            return {
                "risk_level": llm_data.get("risk_level", "medium"),
                "risk_score": llm_data.get("risk_score", 50),
                "high_risk_count": len([r for r in risk_findings if r.get("level") == "HIGH"]),
                "medium_risk_count": len([r for r in risk_findings if r.get("level") == "MEDIUM"]),
                "findings": risk_findings,
                "llm_analysis": llm_data,
                "recommendations": llm_data.get("recommendations", []),
                "next_steps": llm_data.get("next_steps", [])
            }
    except Exception as e:
        print(f"[LLM调用失败] {e}, 使用规则引擎兜底")

    # ========== 规则引擎兜底（LLM失败时） ==========
    # 检查交易风险
    if transactions:
        large_txs = transactions.get("large_transactions", [])
        if large_txs:
            risk_findings.append({
                "type": "大额转账",
                "level": "HIGH",
                "detail": f"发现{len(large_txs)}笔大额转账，单笔最高{_format_amount(max(t['amount'] for t in large_txs))}"
            })

        # 检查频繁交易
        if transactions.get("transaction_count", 0) > 100:
            risk_findings.append({
                "type": "频繁交易",
                "level": "MEDIUM",
                "detail": f"交易笔数较多({transactions.get('transaction_count')}笔)，建议关注"
            })

    # 根据企业风险等级
    risk_level = enterprise_info.get("risk_level", "low")
    if risk_level == "high":
        risk_findings.append({
            "type": "企业风险",
            "level": "HIGH",
            "detail": "该企业在我行风险评级为高风险"
        })
    elif risk_level == "medium":
        risk_findings.append({
            "type": "企业风险",
            "level": "MEDIUM",
            "detail": "该企业在我行风险评级为中等风险"
        })

    # 计算风险得分
    high_count = len([r for r in risk_findings if r["level"] == "HIGH"])
    medium_count = len([r for r in risk_findings if r["level"] == "MEDIUM"])

    if high_count > 0:
        final_risk_level = "high"
    elif medium_count > 0:
        final_risk_level = "medium"
    else:
        final_risk_level = "low"

    return {
        "risk_level": final_risk_level,
        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "findings": risk_findings
    }


def _format_amount(amount: int) -> str:
    """格式化金额"""
    if amount >= 10000:
        return f"{amount/10000:.0f}万"
    return f"{amount}元"


def generate_report(enterprise_info, transactions, risk_analysis):
    """生成报告"""
    return {
        "enterprise": enterprise_info,
        "transactions": transactions,
        "risk_analysis": risk_analysis,
        "summary": {
            "risk_level": risk_analysis["risk_level"],
            "high_risk_count": risk_analysis["high_risk_count"],
            "medium_risk_count": risk_analysis["medium_risk_count"],
            "recommendation": "建议人工复核" if risk_analysis["risk_level"] != "low" else "建议持续监控"
        }
    }


# ==================== Agent流程 ====================

def run_agent_analysis(keyword: str):
    """
    Agent分析主流程

    Step 1: 意图理解 - 解析用户输入
    Step 2: 任务拆解 - 规划执行步骤
    Step 3: 工具调用 - 获取数据+分析
    Step 4: 报告生成 - 输出结果
    """
    steps = []

    # Step 1: 意图理解
    steps.append({"step": "intent", "status": "completed", "message": "意图理解完成 - 解析到企业查询"})
    time.sleep(0.3)

    # Step 2: 任务拆解
    steps.append({"step": "planning", "status": "completed", "message": "任务拆解完成 - 3个子任务"})
    time.sleep(0.3)

    # 查询企业信息
    enterprise_info = query_enterprise(keyword)
    if not enterprise_info:
        return {
            "success": False,
            "error": "未找到该企业信息",
            "steps": steps
        }

    steps.append({"step": "query_enterprise", "status": "completed", "message": f"查询到企业: {enterprise_info['customer_name']}"})
    time.sleep(0.3)

    # 查询交易数据
    customer_no = enterprise_info["customer_no"]
    transactions = query_transactions(customer_no)
    steps.append({"step": "query_transactions", "status": "completed", "message": f"获取到{transactions['transaction_count']}笔交易记录"})
    time.sleep(0.3)

    # 风险分析
    risk_analysis = analyze_risk(enterprise_info, transactions)
    steps.append({"step": "risk_analysis", "status": "completed", "message": f"风险分析完成 - {risk_analysis['risk_level']}风险"})
    time.sleep(0.3)

    # 生成报告
    report = generate_report(enterprise_info, transactions, risk_analysis)
    steps.append({"step": "report", "status": "completed", "message": "报告生成完成"})

    return {
        "success": True,
        "steps": steps,
        "result": report
    }


# ==================== API路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析接口"""
    data = request.get_json()
    keyword = data.get('keyword', '').strip()

    if not keyword:
        return jsonify({"success": False, "error": "请输入查询关键词"})

    result = run_agent_analysis(keyword)
    return jsonify(result)


@app.route('/api/query', methods=['POST'])
def query():
    """查询企业信息"""
    data = request.get_json()
    keyword = data.get('keyword', '').strip()

    if not keyword:
        return jsonify({"success": False, "error": "请输入查询关键词"})

    enterprise = query_enterprise(keyword)
    if enterprise:
        return jsonify({"success": True, "data": enterprise})
    else:
        return jsonify({"success": False, "error": "未找到该企业"})


# ==================== 启动 ====================

if __name__ == '__main__':
    print("=" * 50)
    print("  银行智能尽调Agent系统")
    print("  访问地址: http://localhost:8888")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=8888)
