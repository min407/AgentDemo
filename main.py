"""
银行风险尽调智能分析Agent - 主程序入口
"""
import sys
import time
from llm_client import get_client
from task_decomposer import TaskDecomposer
from tools import ToolExecutor
from dialog_manager import DialogManager, AgentState


class RiskAnalysisAgent:
    """风险尽调分析Agent"""

    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.llm = get_client(use_mock)
        self.decomposer = TaskDecomposer(use_mock)
        self.tool_executor = ToolExecutor()
        self.dialog_manager = DialogManager()

    def process(self, user_query: str, session_id: str = "default") -> str:
        """
        处理用户查询的主流程

        Args:
            user_query: 用户查询
            session_id: 会话ID

        Returns:
            分析结果
        """
        print("\n" + "=" * 60)
        print("  银行风险尽调智能分析Agent")
        print("=" * 60)

        # 创建或获取会话
        session = self.dialog_manager.get_session(session_id)
        if not session:
            session = self.dialog_manager.create_session(session_id)

        # Step 1: 接收问题
        print(f"\n[Step 1] 接收问题")
        print(f"  用户: {user_query}")
        self.dialog_manager.set_query(session_id, user_query)
        self.dialog_manager.update_state(session_id, AgentState.UNDERSTANDING)

        # 提取企业名称（简单正则）
        import re
        company_match = re.search(r'([A-Z])公司|([^\s]+)公司', user_query)
        company_name = company_match.group(1) or company_match.group(2) if company_match else "某企业"
        if company_name == "某企业":
            company_match = re.search(r'([^\s]+)', user_query)
            company_name = company_match.group(1) if company_match else "某企业"
        self.dialog_manager.add_context(session_id, "company_name", company_name)

        # Step 2: 任务拆解
        tasks = self.decomposer.decompose(user_query)
        self.dialog_manager.update_state(session_id, AgentState.DECOMPOSING)

        # Step 3: 执行工具
        print(f"\n[Step 3] 执行工具...")
        print("-" * 40)

        tool_results = {}
        for i, task in enumerate(tasks, 1):
            print(f"\n执行任务 {i}/{len(tasks)}: {task.description}")

            # 调用工具
            params = self._build_params(task.tool, company_name, tool_results)
            result = self.tool_executor.execute(task.tool, params)

            tool_results[task.tool] = result
            self.dialog_manager.store_tool_result(session_id, task.tool, result)

            if result.success:
                print(f"  ✓ {result.message}")
            else:
                print(f"  ✗ {result.message}")

        print("-" * 40)

        # Step 4: 汇总结果
        print(f"\n[Step 4] 汇总结果，生成报告...")
        self.dialog_manager.update_state(session_id, AgentState.SUMMARIZING)

        # 构建分析结果摘要
        analysis_summary = {
            "company_name": company_name,
            "total_income": 0,
            "total_expense": 0,
            "transaction_count": 0,
            "high_risk": 0,
            "medium_risk": 0,
        }

        # 合并交易数据
        trade_result = tool_results.get("trade_api")
        if trade_result and trade_result.success:
            data = trade_result.data
            analysis_summary["total_income"] = data.get("total_income", 0)
            analysis_summary["total_expense"] = data.get("total_expense", 0)
            analysis_summary["transaction_count"] = data.get("transaction_count", 0)

        # 合并风险数据
        risk_result = tool_results.get("risk_rules")
        if risk_result and risk_result.success:
            data = risk_result.data
            analysis_summary["high_risk"] = data.get("high_risk", 0)
            analysis_summary["medium_risk"] = data.get("medium_risk", 0)

        # 生成最终报告
        final_report = self._generate_report(analysis_summary, tool_results)

        self.dialog_manager.update_state(session_id, AgentState.COMPLETED)
        self.dialog_manager.add_response(session_id, final_report)

        return final_report

    def _build_params(self, tool_name: str, company_name: str, previous_results: dict) -> dict:
        """构建工具参数"""
        params = {}

        if tool_name == "trade_api":
            params = {"company_name": company_name, "days": 90}

        elif tool_name == "risk_rules":
            trade_data = previous_results.get("trade_api")
            params = {"trade_data": trade_data.data if trade_data else {}}

        elif tool_name == "rag":
            params = {"query": "反洗钱 大额交易 可疑交易"}

        elif tool_name == "report_gen":
            # 汇总所有结果
            report_data = {}
            for tool_name, result in previous_results.items():
                if result.success:
                    report_data[tool_name] = result.data
            report_data["company_name"] = company_name
            params = report_data

        return params

    def _generate_report(self, summary: dict, tool_results: dict) -> str:
        """生成最终报告"""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("  分析报告")
        lines.append("=" * 60)

        lines.append(f"\n【企业基本信息】")
        lines.append(f"  企业名称: {summary['company_name']}")
        lines.append(f"  分析周期: 近3个月")

        lines.append(f"\n【交易数据分析】")
        lines.append(f"  累计收入: {summary['total_income']/10000:.0f} 万元")
        lines.append(f"  累计支出: {summary['total_expense']/10000:.0f} 万元")
        lines.append(f"  交易笔数: {summary['transaction_count']} 笔")

        lines.append(f"\n【风险评估结果】")
        lines.append(f"  🔴 高风险点: {summary['high_risk']} 个")
        lines.append(f"  🟡 中风险点: {summary['medium_risk']} 个")

        # 添加风险详情
        risk_result = tool_results.get("risk_rules")
        if risk_result and risk_result.success:
            lines.append(f"\n【风险详情】")
            for risk in risk_result.data.get("risk_details", [])[:3]:
                level_icon = "🔴" if risk["risk_level"] == "HIGH" else "🟡"
                lines.append(f"  {level_icon} {risk['type']}: {risk['detail']}")

        lines.append(f"\n【结论与建议】")
        if summary['high_risk'] > 0:
            lines.append(f"  ⚠️ 该企业存在{summary['high_risk']}个高风险点，")
            lines.append(f"     建议进行人工复核，重点关注大额转账和夜间交易。")
        else:
            lines.append(f"  ✓ 未发现明显风险点，建议持续监控。")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "=" * 60)
    print("  银行风险尽调智能分析Agent - 演示系统")
    print("  Version B: 基础版 (带Agent流程)")
    print("=" * 60)
    print("\n功能说明:")
    print("  - 任务拆解: 将复杂问题拆解为子任务")
    print("  - 工具调用: 模拟交易API、风险规则库、RAG系统")
    print("  - 状态管理: 全流程状态追踪")
    print("  - 报告生成: 自动汇总分析结果")
    print("\n输入示例:")
    print("  - 请分析A公司近三个月的交易流水")
    print("  - 帮我看看B企业的风险情况")
    print("  - 对C公司做个尽调报告")
    print("\n输入 'quit' 或 'q' 退出")
    print("=" * 60)


def main():
    """主函数"""
    print_welcome()

    # 创建Agent实例（使用模拟LLM）
    agent = RiskAnalysisAgent(use_mock=True)

    session_id = "demo_session"

    while True:
        try:
            user_input = input("\n请输入分析任务: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "q", "exit"]:
                print("\n感谢使用，再见！")
                break

            # 处理查询
            result = agent.process(user_input, session_id)

            # 打印结果
            print(result)

        except KeyboardInterrupt:
            print("\n\n已退出")
            break
        except Exception as e:
            print(f"\n错误: {str(e)}")
            print("请重试...")


if __name__ == "__main__":
    main()
