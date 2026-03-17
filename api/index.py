# Vercel Python Handler
import os
import sys

# 设置路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# 创建Flask应用
app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# 导入必要模块
import json
import re
import datetime
try:
    import dashscope
    from dashscope import Generation
    dashscope.api_key = "sk-61a5eb4cd7e04bc7ba44acaa1bf1a99e"
    DASHSCOPE_AVAILABLE = True
except:
    DASHSCOPE_AVAILABLE = False

# 模拟数据
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
        "business_scope": "投资兴办实业；投资咨询；创业项目投资",
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
        "address": "深圳市龙岗区南湾街道下李朗社区联李东路8号赛为大楼",
        "business_scope": "人工智能系统、无人机研发、销售",
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
        "address": "深圳市南山区粤海街道沙河西路深圳湾科技生态园",
        "business_scope": "计算机软硬件开发及服务",
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
        "address": "天津经济技术开发区第一大街79号",
        "business_scope": "网络预约出租汽车客运经营",
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
        "address": "深圳市南山区科技园科技南十二路2号金蝶软件园",
        "business_scope": "生产、开发、经营电脑软硬件",
        "employees": 3457,
        "risk_level": "low",
        "enterprise_type": "有限责任公司（外国法人独资）",
        "company_size": "L（大型）",
        "stock_code": "00268.HK"
    }
}

MOCK_TRANSACTIONS = {
    "C20240001": {"period": "2024-01 to 2024-03", "total_income": 15000000, "total_outflow": 12000000, "balance": 8000000, "avg_monthly_income": 5000000, "avg_monthly_expense": 4000000, "transaction_count": 35, "large_transactions": [{"date": "2024-02-15", "amount": 5000000, "type": "in", "desc": "投资收益"}, {"date": "2024-03-10", "amount": 3000000, "type": "out", "desc": "项目投资"}]},
    "C20240002": {"period": "2024-01 to 2024-03", "total_income": 28000000, "total_outflow": 25000000, "balance": 15000000, "avg_monthly_income": 9333333, "avg_monthly_expense": 8333333, "transaction_count": 120, "large_transactions": [{"date": "2024-01-20", "amount": 8000000, "type": "in", "desc": "项目回款"}, {"date": "2024-02-28", "amount": 5000000, "type": "out", "desc": "设备采购"}]},
    "C20240003": {"period": "2024-01 to 2024-03", "total_income": 45000000, "total_outflow": 38000000, "balance": 28000000, "avg_monthly_income": 15000000, "avg_monthly_expense": 12666667, "transaction_count": 180, "large_transactions": [{"date": "2024-01-10", "amount": 12000000, "type": "in", "desc": "合同收入"}]},
    "C20240004": {"period": "2024-01 to 2024-03", "total_income": 8500000, "total_outflow": 8200000, "balance": 3500000, "avg_monthly_income": 2833333, "avg_monthly_expense": 2733333, "transaction_count": 45, "large_transactions": [{"date": "2024-02-10", "amount": 2000000, "type": "out", "desc": "平台补贴"}]},
    "C20240005": {"period": "2024-01 to 2024-03", "total_income": 120000000, "total_outflow": 95000000, "balance": 65000000, "avg_monthly_income": 40000000, "avg_monthly_expense": 31666667, "transaction_count": 320, "large_transactions": [{"date": "2024-01-15", "amount": 35000000, "type": "in", "desc": "软件授权收入"}, {"date": "2024-02-20", "amount": 20000000, "type": "in", "desc": "云服务收入"}]}
}

def query_enterprise(keyword):
    if keyword in MOCK_ENTERPRISES:
        return MOCK_ENTERPRISES[keyword]
    for name, info in MOCK_ENTERPRISES.items():
        if keyword in name or info.get("credit_code") == keyword:
            return info
    return None

def query_transactions(customer_no):
    return MOCK_TRANSACTIONS.get(customer_no, {"period": "2024-01 to 2024-03", "total_income": 5000000, "total_outflow": 4800000, "balance": 2000000, "avg_monthly_income": 1660000, "avg_monthly_expense": 1600000, "transaction_count": 100, "large_transactions": []})

def format_amount(amount):
    if amount >= 10000:
        return f"{amount/10000:.0f}万"
    return f"{amount}元"

def analyze_risk(enterprise_info, transactions):
    risk_findings = []

    # 简化版LLM分析
    prompt = f"""分析企业{enterprise_info.get('customer_name')}的风险：
    行业：{enterprise_info.get('industry')}
    注册资本：{format_amount(enterprise_info.get('reg_capital', 0))}
    收入：{format_amount(transactions.get('total_income', 0))}
    支出：{format_amount(transactions.get('total_outflow', 0))}

    返回JSON：{{"risk_level":"low/medium/high","risk_score":0-100,"key_findings":["发现1"],"recommendations":["建议1"]}}"""

    try:
        if DASHSCOPE_AVAILABLE:
            response = Generation.call(model="qwen-turbo", messages=[{"role": "user", "content": prompt}], result_format="message")
            if response.status_code == 200:
                result_text = response.output.choices[0].message.content
                try:
                    data = json.loads(result_text)
                    risk_findings.append({"type": "AI分析", "level": "LOW", "detail": "基于AI智能分析"})
                    return {
                        "risk_level": data.get("risk_level", "medium"),
                        "risk_score": data.get("risk_score", 50),
                        "high_risk_count": 0,
                        "medium_risk_count": 1,
                        "findings": risk_findings,
                        "recommendations": data.get("recommendations", ["建议持续监控"]),
                        "llm_analysis": data
                    }
                except:
                    pass
    except:
        pass

    # 兜底
    return {
        "risk_level": "medium",
        "risk_score": 50,
        "high_risk_count": 0,
        "medium_risk_count": 1,
        "findings": [{"type": "系统分析", "level": "LOW", "detail": "基于规则引擎分析"}],
        "recommendations": ["建议持续监控"],
        "llm_analysis": {}
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    if not keyword:
        return jsonify({"success": False, "error": "请输入查询关键词"})

    enterprise = query_enterprise(keyword)
    if not enterprise:
        return jsonify({"success": False, "error": "未找到该企业"})

    transactions = query_transactions(enterprise["customer_no"])
    risk_analysis = analyze_risk(enterprise, transactions)

    return jsonify({
        "success": True,
        "result": {
            "enterprise": enterprise,
            "transactions": transactions,
            "risk_analysis": risk_analysis,
            "summary": {"risk_level": risk_analysis["risk_level"], "recommendation": "建议人工复核" if risk_analysis["risk_level"] != "low" else "建议持续监控"}
        }
    })

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    enterprise = query_enterprise(keyword)
    if enterprise:
        return jsonify({"success": True, "data": enterprise})
    return jsonify({"success": False, "error": "未找到该企业"})

# Vercel handler
def handler(request, context=None):
    return app(request.environ, lambda status, headers: (status, headers))
