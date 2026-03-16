"""
银行智能尽调Agent - Flask Web服务
"""
import json
import re
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==================== 模拟数据 ====================
MOCK_ENTERPRISES = {
    "A公司": {
        "credit_code": "91110000MA7A8XXXXX",
        "customer_no": "C20240001",
        "customer_name": "A公司",
        "legal_person": "张三",
        "reg_capital": 10000000,
        "establish_date": "2018-03-15",
        "industry": "软件开发",
        "address": "北京市海淀区中关村",
        "business_scope": "软件开发、技术咨询",
        "employees": 50,
        "risk_level": "medium"
    },
    "B科技有限公司": {
        "credit_code": "91310000MB2XXXXX",
        "customer_no": "C20240002",
        "customer_name": "B科技有限公司",
        "legal_person": "李四",
        "reg_capital": 5000000,
        "establish_date": "2020-06-20",
        "industry": "信息技术",
        "address": "上海市浦东新区",
        "business_scope": "软件开发、系统集成",
        "employees": 30,
        "risk_level": "low"
    },
    "C实业集团": {
        "credit_code": "91440000MACXXXXX",
        "customer_no": "C20240003",
        "customer_name": "C实业集团",
        "legal_person": "王五",
        "reg_capital": 500000000,
        "establish_date": "2010-01-10",
        "industry": "房地产",
        "address": "广州市天河区",
        "business_scope": "房地产开发、物业管理",
        "employees": 500,
        "risk_level": "high"
    }
}

# 模拟交易数据
MOCK_TRANSACTIONS = {
    "C20240001": {
        "period": "2024-01 to 2024-03",
        "total_income": 8500000,
        "total_outflow": 8200000,
        "balance": 3500000,
        "avg_monthly_income": 2800000,
        "avg_monthly_expense": 2730000,
        "transaction_count": 156,
        "large_transactions": [
            {"date": "2024-02-15", "amount": 2000000, "type": "out", "desc": "设备采购"},
            {"date": "2024-03-10", "amount": 1500000, "type": "in", "desc": "项目回款"}
        ]
    },
    "C20240002": {
        "period": "2024-01 to 2024-03",
        "total_income": 3200000,
        "total_outflow": 2800000,
        "balance": 1200000,
        "avg_monthly_income": 1060000,
        "avg_monthly_expense": 933000,
        "transaction_count": 45,
        "large_transactions": []
    },
    "C20240003": {
        "period": "2024-01 to 2024-03",
        "total_income": 15000000,
        "total_outflow": 14500000,
        "balance": 8000000,
        "avg_monthly_income": 5000000,
        "avg_monthly_expense": 4830000,
        "transaction_count": 280,
        "large_transactions": [
            {"date": "2024-01-20", "amount": 5000000, "type": "out", "desc": "土地款支付"},
            {"date": "2024-02-15", "amount": 3000000, "type": "out", "desc": "工程款"}
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
    """风险分析"""
    risk_findings = []

    # 检查交易风险
    if transactions:
        large_txs = transactions.get("large_transactions", [])
        if large_txs:
            risk_findings.append({
                "type": "大额转账",
                "level": "HIGH",
                "detail": f"发现{len(large_txs)}笔大额转账，单笔最高{_format_amount(max(t['amount'] for t in large_txs))}"
            })

        # 检查夜间交易（模拟）
        if transactions.get("transaction_count", 0) > 100:
            risk_findings.append({
                "type": "频繁交易",
                "level": "MEDIUM",
                "detail": f"交易笔数较多({transactions.get('transaction_count')}笔)，建议关注"
            })

    # 根据企业风险等级添加风险
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
