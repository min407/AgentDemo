"""
工具调用模块 - 模拟银行各种API和系统
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import time


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_name: str
    success: bool
    data: Dict
    message: str


class TradeQueryAPI:
    """交易数据查询API"""

    def __init__(self):
        self.name = "交易查询API"

    def call(self, company_name: str, days: int = 90) -> ToolResult:
        """查询企业交易流水"""
        print(f"\n[工具调用] {self.name}")
        print(f"  参数: 企业名称={company_name}, 查询天数={days}天")

        # 模拟API调用延迟
        time.sleep(0.5)

        # 返回模拟数据
        data = {
            "company_name": company_name,
            "period": f"近{days}天",
            "total_income": 5000000,  # 500万
            "total_expense": 4800000,  # 480万
            "transaction_count": 156,
            "max_single_amount": 800000,  # 80万
            "transactions": [
                {"date": "2025-01-15", "amount": 800000, "type": "收入", "counterparty": "B公司"},
                {"date": "2025-01-20", "amount": 600000, "type": "支出", "counterparty": "C公司"},
                {"date": "2025-02-05", "amount": 550000, "type": "收入", "counterparty": "D公司"},
                {"date": "2025-02-10", "amount": 700000, "type": "支出", "counterparty": "E公司"},
                {"date": "2025-02-15", "amount": 300000, "type": "收入", "counterparty": "个人"},
            ]
        }

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=data,
            message=f"成功查询到{company_name}的{len(data['transactions'])}笔交易记录"
        )


class RiskRuleEngine:
    """风险规则引擎"""

    def __init__(self):
        self.name = "风险规则库"
        self.rules = {
            "大额转账": {"threshold": 500000, "risk_level": "HIGH"},
            "频繁交易": {"threshold": 20, "risk_level": "MEDIUM"},
            "夜间交易": {"time_range": "22:00-05:00", "risk_level": "MEDIUM"},
            "分散转入集中转出": {"ratio": 0.8, "risk_level": "HIGH"},
            "资金快进快出": {"retention_days": 1, "risk_level": "HIGH"},
        }

    def call(self, trade_data: Dict) -> ToolResult:
        """匹配风险规则"""
        print(f"\n[工具调用] {self.name}")

        risks = []

        # 检查大额转账
        for tx in trade_data.get("transactions", []):
            if tx["amount"] >= 500000:
                risks.append({
                    "type": "大额转账",
                    "risk_level": "HIGH",
                    "detail": f"单笔{tx['amount']/10000:.0f}万转账",
                    "transaction": tx
                })

        # 检查夜间交易（模拟）
        risks.append({
            "type": "夜间交易",
            "risk_level": "MEDIUM",
            "detail": "发现12笔夜间交易(22:00-05:00)"
        })

        # 检查资金快进快出（模拟）
        risks.append({
            "type": "资金快进快出",
            "risk_level": "HIGH",
            "detail": "T+1日转出比例超过80%"
        })

        data = {
            "total_risks": len(risks),
            "high_risk": len([r for r in risks if r["risk_level"] == "HIGH"]),
            "medium_risk": len([r for r in risks if r["risk_level"] == "MEDIUM"]),
            "risk_details": risks
        }

        print(f"  发现 {data['high_risk']} 个高风险, {data['medium_risk']} 个中风险")

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=data,
            message=f"发现{len(risks)}个风险点"
        )


class RAGSystem:
    """RAG知识检索系统"""

    def __init__(self):
        self.name = "制度知识检索系统"

        # 模拟知识库
        self.knowledge_base = {
            "反洗钱": "根据《反洗钱法》第十七条，金融机构应当建立健全反洗钱内部控制制度。",
            "大额交易": "根据《金融机构大额交易和可疑交易报告管理办法》，单笔或累计交易超过20万元需上报。",
            "可疑交易": "客户资金来源不明、频繁分散转入集中转出等行为属于可疑交易。",
            "客户尽职调查": "金融机构应当对客户身份进行尽职调查，了解客户及其交易目的。",
        }

    def call(self, query: str) -> ToolResult:
        """检索相关制度条款"""
        print(f"\n[工具调用] {self.name}")
        print(f"  查询: {query}")

        # 模拟检索
        time.sleep(0.3)

        results = []
        for key, value in self.knowledge_base.items():
            if key in query or any(k in query for k in key):
                results.append({"keyword": key, "content": value})

        if not results:
            results = [{"keyword": "general", "content": "未找到相关制度条款，建议人工查阅"}]

        data = {
            "query": query,
            "results": results,
            "total": len(results)
        }

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=data,
            message=f"检索到{len(results)}条相关制度"
        )


class ReportGenerator:
    """报告生成模块"""

    def __init__(self):
        self.name = "报告生成模块"

    def call(self, analysis_results: Dict) -> ToolResult:
        """生成尽调报告"""
        print(f"\n[工具调用] {self.name}")

        report = {
            "title": "企业风险尽调分析报告",
            "sections": [
                {
                    "name": "一、企业基本信息",
                    "content": f"企业名称：{analysis_results.get('company_name', '某企业')}\n分析周期：近3个月"
                },
                {
                    "name": "二、交易数据分析",
                    "content": f"累计收入：{analysis_results.get('total_income', 0)/10000:.0f}万元\n累计支出：{analysis_results.get('total_expense', 0)/10000:.0f}万元\n交易笔数：{analysis_results.get('transaction_count', 0)}笔"
                },
                {
                    "name": "三、风险评估结果",
                    "content": f"高风险点：{analysis_results.get('high_risk', 0)}个\n中风险点：{analysis_results.get('medium_risk', 0)}个"
                },
                {
                    "name": "四、结论与建议",
                    "content": "建议对该企业进行人工复核，重点关注大额转账和夜间交易。"
                }
            ]
        }

        return ToolResult(
            tool_name=self.name,
            success=True,
            data=report,
            message="报告生成完成"
        )


class ToolExecutor:
    """工具执行器"""

    def __init__(self):
        self.tools = {
            "trade_api": TradeQueryAPI(),
            "risk_rules": RiskRuleEngine(),
            "rag": RAGSystem(),
            "report_gen": ReportGenerator(),
        }

    def execute(self, tool_name: str, params: Dict = None) -> ToolResult:
        """
        执行工具

        Args:
            tool_name: 工具名称
            params: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                data={},
                message=f"未找到工具: {tool_name}"
            )

        tool = self.tools[tool_name]

        # 根据不同工具调用
        if tool_name == "trade_api":
            return tool.call(
                company_name=params.get("company_name", "某企业") if params else "某企业",
                days=params.get("days", 90) if params else 90
            )
        elif tool_name == "risk_rules":
            return tool.call(params.get("trade_data", {}) if params else {})
        elif tool_name == "rag":
            return tool.call(params.get("query", "") if params else "")
        elif tool_name == "report_gen":
            return tool.call(params or {})

        return ToolResult(tool_name=tool_name, success=False, data={}, message="未知工具")


if __name__ == "__main__":
    # 测试
    executor = ToolExecutor()

    # 测试交易查询
    result = executor.execute("trade_api", {"company_name": "A公司", "days": 90})
    print(f"结果: {result.message}")

    # 测试风险规则
    result = executor.execute("risk_rules", {"trade_data": result.data})
    print(f"结果: {result.message}")
