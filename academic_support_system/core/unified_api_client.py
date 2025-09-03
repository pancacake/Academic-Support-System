"""
统一的API客户端
"""
import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from .api_config import api_config

logger = logging.getLogger(__name__)

class UnifiedAPIClient:
    """统一的API客户端"""
    
    def __init__(self):
        self.config = api_config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化OpenAI客户端"""
        if not self.config.is_configured():
            logger.warning("API未配置，将使用模拟模式")
            return
            
        try:
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            logger.info("API客户端初始化成功")
        except Exception as e:
            logger.error(f"API客户端初始化失败: {e}")
            self._client = None
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        return self._client is not None and self.config.is_configured()
    
    def call_api(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        timeout: int = 60
    ) -> str:
        """调用API生成文本"""
        if not self.is_available():
            logger.error("API服务不可用，检查配置")
            # 提供模拟响应用于测试
            return self._get_mock_response(prompt)

        if model is None:
            model = self.config.default_model

        try:
            logger.info(f"调用API，模型: {model}, 提示词长度: {len(prompt)}")

            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )

            # 兼容不同的响应格式
            if isinstance(response, str):
                result = response.strip()
            else:
                result = response.choices[0].message.content.strip()

            logger.info(f"API调用成功，响应长度: {len(result)}")
            return result

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"API调用失败: {error_type}: {error_msg}")

            # 检查是否是连接错误
            if "Connection" in error_type or "connection" in error_msg.lower():
                logger.error("检测到连接错误，可能的原因：")
                logger.error("1. 网络连接问题")
                logger.error("2. API服务器不可达")
                logger.error("3. 防火墙阻止连接")
                logger.error(f"API URL: {self.config.base_url}")

            # 在API失败时提供备用响应
            logger.warning("API调用失败，使用模拟响应作为备用方案")
            return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        """获取模拟响应（用于API不可用时）"""
        logger.warning("使用模拟响应")

        # 根据提示词类型返回不同的模拟响应
        if "选择题" in prompt:
            return '''```json
{
    "text": "这是一道模拟选择题，用于测试系统功能。",
    "type": "选择题",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "A",
    "explanation": "这是模拟解析，实际使用时请配置正确的API。"
}
```'''
        elif "填空题" in prompt:
            return '''```json
{
    "text": "这是一道模拟填空题：请填写______。",
    "type": "填空题",
    "answer": "答案",
    "explanation": "这是模拟解析，实际使用时请配置正确的API。"
}
```'''
        elif "判断题" in prompt:
            return '''```json
{
    "text": "这是一道模拟判断题。",
    "type": "判断题",
    "options": ["A. 正确", "B. 错误"],
    "answer": "A",
    "explanation": "这是模拟解析，实际使用时请配置正确的API。"
}
```'''
        elif "解答题" in prompt:
            return '''```json
{
    "text": "这是一道模拟解答题。",
    "type": "解答题",
    "answer": "这是模拟答案。",
    "explanation": "这是模拟解析，实际使用时请配置正确的API。"
}
```'''
        else:
            return "这是一个模拟响应，请配置正确的API密钥。"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """聊天完成API"""
        if not self.is_available():
            raise Exception("API服务不可用")
        
        if model is None:
            model = self.config.default_model
        
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if isinstance(response, str):
                return response.strip()
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"聊天API调用失败: {e}")
            raise Exception(f"聊天API调用失败: {str(e)}")
    
    def generate_questions_with_prompt(
        self,
        prompt: str,
        expected_format: str = "json"
    ) -> Dict[str, Any]:
        """使用提示词生成题目"""
        try:
            response = self.call_api(prompt)
            
            if expected_format == "json":
                # 尝试解析JSON响应
                try:
                    # 提取JSON部分
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = response
                    
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning("JSON解析失败，返回原始响应")
                    return {"raw_response": response}
            
            return {"response": response}
            
        except Exception as e:
            logger.error(f"生成题目失败: {e}")
            raise

# 全局客户端实例
unified_client = UnifiedAPIClient()
