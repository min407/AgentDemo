"""
对话状态管理模块
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


class AgentState(Enum):
    """Agent状态"""
    IDLE = "idle"  # 空闲
    UNDERSTANDING = "understanding"  # 理解问题
    DECOMPOSING = "decomposing"  # 任务拆解
    EXECUTING = "executing"  # 执行工具
    SUMMARIZING = "summarizing"  # 汇总结果
    COMPLETED = "completed"  # 完成
    ERROR = "error"  # 错误


@dataclass
class Message:
    """对话消息"""
    role: str  # user, assistant, system
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Session:
    """会话状态"""
    session_id: str
    user_id: str = "default"
    state: AgentState = AgentState.IDLE
    current_query: str = ""
    tasks: List = field(default_factory=list)
    tool_results: Dict = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)
    context: Dict = field(default_factory=dict)  # 存储提取的实体等
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append(Message(role=role, content=content))
        self.updated_at = time.time()

    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史消息"""
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        return [{"role": m.role, "content": m.content} for m in recent]


class DialogManager:
    """对话管理器"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, session_id: str, user_id: str = "default") -> Session:
        """创建新会话"""
        session = Session(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)

    def update_state(self, session_id: str, state: AgentState):
        """更新会话状态"""
        session = self.get_session(session_id)
        if session:
            session.state = state
            session.updated_at = time.time()

    def set_query(self, session_id: str, query: str):
        """设置用户查询"""
        session = self.get_session(session_id)
        if session:
            session.current_query = query
            session.add_message("user", query)

    def add_context(self, session_id: str, key: str, value: any):
        """添加上下文"""
        session = self.get_session(session_id)
        if session:
            session.context[key] = value

    def get_context(self, session_id: str, key: str) -> any:
        """获取上下文"""
        session = self.get_session(session_id)
        if session:
            return session.context.get(key)
        return None

    def store_tool_result(self, session_id: str, tool_name: str, result: any):
        """存储工具执行结果"""
        session = self.get_session(session_id)
        if session:
            session.tool_results[tool_name] = result

    def get_tool_result(self, session_id: str, tool_name: str) -> any:
        """获取工具执行结果"""
        session = self.get_session(session_id)
        if session:
            return session.tool_results.get(tool_name)
        return None

    def add_response(self, session_id: str, response: str):
        """添加助手回复"""
        session = self.get_session(session_id)
        if session:
            session.add_message("assistant", response)

    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())


if __name__ == "__main__":
    # 测试
    dm = DialogManager()
    session = dm.create_session("test_001")

    dm.set_query("test_001", "请分析A公司")
    dm.update_state("test_001", AgentState.DECOMPOSING)
    dm.add_context("test_001", "company_name", "A公司")

    print(f"会话状态: {session.state}")
    print(f"查询: {session.current_query}")
    print(f"上下文: {session.context}")
    print(f"历史消息: {session.get_history()}")
