"""
通义千问API调用模块
"""
import json
from typing import Optional, List, Dict

try:
    import dashscope
    from dashscope import Generation
    from config import DASHSCOPE_API_KEY, QWEN_MODEL
    # 设置API Key
    dashscope.api_key = DASHSCOPE_API_KEY
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    QWEN_MODEL = "qwen-turbo"


class QwenClient:
    """通义千问API客户端"""

    def __init__(self, model: str = QWEN_MODEL):
        self.model = model

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用通义千问API

        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）

        Returns:
            API返回的文本内容
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message"
            )
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"[API错误] {response.code}: {response.message}"
        except Exception as e:
            return f"[调用失败] {str(e)}"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        多轮对话接口

        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]

        Returns:
            助手回复
        """
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message"
            )
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"[API错误] {response.code}: {response.message}"
        except Exception as e:
            return f"[调用失败] {str(e)}"


class MockQwenClient:
    """模拟的通义千问客户端（用于测试）"""

    def __init__(self):
        self.model = "mock"

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """模拟调用，返回预设响应"""
        if "拆解" in prompt or "任务" in prompt:
            return """我将这个任务拆解为3个子任务：
1. 交易数据查询 - 调用交易查询API获取该企业近3个月的交易流水
2. 风险规则匹配 - 查询风险规则库，识别可疑交易特征
3. 制度条款比对 - 通过RAG系统检索相关合规要求"""

        if "交易" in prompt or "流水" in prompt:
            return """根据交易查询API返回的数据：
- 近3个月累计收入：500万元
- 近3个月累计支出：480万元
- 交易笔数：156笔
- 最大单笔金额：80万元"""

        if "风险" in prompt or "规则" in prompt:
            return """风险规则匹配结果：
- 发现1个高风险点：单笔超50万大额转账（3笔）
- 发现1个中风险点：夜间交易（22:00-05:00）共12笔
- 建议：需人工复核"""

        if "制度" in prompt or "合规" in prompt:
            return """根据《反洗钱法》和《金融机构大额交易和可疑交易报告管理办法》：
- 该企业交易符合大额可疑交易报告标准
- 建议按照规定提交可疑交易报告"""

        return "我理解了你的请求，正在处理中..."

    def chat(self, messages: List[Dict[str, str]]) -> str:
        return self.call(messages[-1]["content"])


def get_client(use_mock: bool = False) -> "QwenClient | MockQwenClient":
    """获取客户端实例"""
    if use_mock:
        return MockQwenClient()
    return QwenClient()


if __name__ == "__main__":
    # 测试
    client = MockQwenClient()
    result = client.call("请帮我分析A公司的风险")
    print(result)
