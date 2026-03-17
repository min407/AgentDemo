"""
银行风险尽调智能分析Agent - 配置文件
"""
import os

# 通义千问API配置
DASHSCOPE_API_KEY = "sk-61a5eb4cd7e04bc7ba44acaa1bf1a99e"  # API Key
QWEN_MODEL = "qwen-turbo"  # 可选: qwen-turbo, qwen-plus, qwen-max

# 银行知识库配置
KNOWLEDGE_BASE_PATH = "data/knowledge_base.json"

# 风险规则配置
RISK_RULES = {
    "大额转账": {"threshold": 500000, "risk_level": "HIGH"},
    "频繁交易": {"threshold": 20, "risk_level": "MEDIUM"},
    "夜间交易": {"time_range": "22:00-05:00", "risk_level": "MEDIUM"},
    "分散转入集中转出": {"ratio": 0.8, "risk_level": "HIGH"},
    "资金快进快出": {"retention_days": 1, "risk_level": "HIGH"},
}

# 对话配置
MAX_TURN = 10  # 最大对话轮次
SESSION_TIMEOUT = 300  # 会话超时时间（秒）
