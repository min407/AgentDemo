"""
任务拆解模块 - ReAct风格任务规划
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from llm_client import get_client


@dataclass
class Task:
    """任务实体"""
    task_id: str
    description: str
    tool: str  # 需要调用的工具
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None


class TaskDecomposer:
    """任务拆解器 - 将用户问题拆解为可执行的子任务"""

    # 预定义的任务模板
    TASK_TEMPLATES = {
        "交易分析": [
            {"tool": "trade_api", "description": "查询交易数据"},
            {"tool": "risk_rules", "description": "匹配风险规则"},
            {"tool": "rag", "description": "检索合规制度"}
        ],
        "风险评估": [
            {"tool": "risk_rules", "description": "评估风险等级"},
            {"tool": "rag", "description": "检索相关政策"}
        ],
        "尽调报告": [
            {"tool": "trade_api", "description": "获取经营数据"},
            {"tool": "risk_rules", "description": "识别风险点"},
            {"tool": "report_gen", "description": "生成报告"}
        ]
    }

    def __init__(self, use_mock: bool = True):
        self.llm = get_client(use_mock)
        self.use_mock = use_mock

    def decompose(self, user_query: str) -> List[Task]:
        """
        拆解用户问题为子任务

        Args:
            user_query: 用户查询

        Returns:
            任务列表
        """
        print(f"\n[Step 2] 任务拆解...")
        print("-" * 40)

        # 调用LLM进行任务拆解
        system_prompt = """你是一个银行风险尽调Agent的任务规划助手。
用户的查询通常是关于企业风险分析、交易流水分析等。
请将任务拆解为具体的子任务，只返回子任务列表，不需要其他内容。

可用的工具：
- trade_api: 交易数据查询API
- risk_rules: 风险规则匹配系统
- rag: 制度知识检索系统
- report_gen: 报告生成模块

请按以下格式返回：
任务1|工具名|任务描述
任务2|工具名|任务描述
任务3|工具名|任务描述"""

        prompt = f"用户问题：{user_query}\n请拆解这个任务"

        response = self.llm.call(prompt, system_prompt)

        # 解析任务
        tasks = self._parse_tasks(response)

        if not tasks:
            # 使用默认模板
            tasks = self._use_template(user_query)

        # 打印任务列表
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.description} (调用工具: {task.tool})")

        print("-" * 40)

        return tasks

    def _parse_tasks(self, response: str) -> List[Task]:
        """解析LLM返回的任务列表"""
        tasks = []
        lines = response.strip().split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 尝试解析格式：序号. 任务描述 (工具: xxx)
            parts = line.split("|")
            if len(parts) >= 3:
                task = Task(
                    task_id=f"task_{i+1}",
                    description=parts[2].strip(),
                    tool=parts[1].strip()
                )
                tasks.append(task)
            elif "调用工具" in line or "tool" in line.lower():
                # 简单解析
                desc = line.split(".")[-1].strip() if "." in line else line
                task = Task(
                    task_id=f"task_{i+1}",
                    description=desc,
                    tool="unknown"
                )
                tasks.append(task)

        return tasks

    def _use_template(self, query: str) -> List[Task]:
        """使用预定义模板"""
        # 根据关键词匹配模板
        query_keywords = query.lower()

        if "分析" in query_keywords or "流水" in query_keywords:
            template = self.TASK_TEMPLATES["交易分析"]
        elif "风险" in query_keywords:
            template = self.TASK_TEMPLATES["风险评估"]
        elif "报告" in query_keywords:
            template = self.TASK_TEMPLATES["尽调报告"]
        else:
            # 默认模板
            template = self.TASK_TEMPLATES["交易分析"]

        tasks = []
        for i, t in enumerate(template):
            tasks.append(Task(
                task_id=f"task_{i+1}",
                description=t["description"],
                tool=t["tool"]
            ))

        return tasks


if __name__ == "__main__":
    # 测试
    decomposer = TaskDecomposer(use_mock=True)
    tasks = decomposer.decompose("请分析A公司近三个月的交易流水")
    print(f"\n共拆解出 {len(tasks)} 个任务")
