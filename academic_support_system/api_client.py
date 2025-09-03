import base64
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import OpenAI

class APIClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "your_urls",
        default_model: str = "your_model"
    ):
        """
        Initializes the API client.
        Args:
            api_key: Your API key
            base_url: The base URL for the API (default is the proxy URL)
            default_model: Default model to use for requests
        """
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def call_api(
        self,
        prompt: str,
        image_paths: Optional[List[str]] = None,
        model: Optional[str] = None,
        max_tokens: int = 50000,
        temperature: float = 0.7,
        timeout: int = 60
    ) -> str:
        if model is None:
            model = self.default_model
            
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
        
        if image_paths:
            for path in image_paths:
                try:
                    with open(path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    })
                except Exception as e:
                    raise ValueError(f"Failed to process image {path}: {str(e)}")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )
            # 兼容代理/SDK返回字符串或OpenAI对象
            if isinstance(response, str):
                return response.strip()
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")

    def call_api_streaming(
        self,
        prompt: str,
        image_paths: Optional[List[str]] = None,
        model: Optional[str] = None,
        max_tokens: int = 20000,
        temperature: float = 0.7,
        timeout: int = 60
    ):
        """
        流式请求API，返回生成器。
        prompt: 用户输入文本
        image_paths: 可选图片路径列表
        其余参数同call_api
        返回: openai流式响应生成器
        """
        if model is None:
            model = self.default_model
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
        if image_paths:
            for path in image_paths:
                try:
                    with open(path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    })
                except Exception as e:
                    raise ValueError(f"Failed to process image {path}: {str(e)}")
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                stream=True
            )
            return stream
        except Exception as e:
            raise Exception(f"Streaming API call failed: {str(e)}")