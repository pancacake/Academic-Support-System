"""
统一的错误处理机制
"""
import logging
import traceback
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandler:
    """统一的错误处理器"""
    
    @staticmethod
    def handle_api_error(error, context="API调用"):
        """处理API错误"""
        error_msg = str(error)
        logger.error(f"{context}失败: {error_msg}")
        
        # 在开发环境下提供更详细的错误信息
        if settings.DEBUG:
            logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        # 根据错误类型返回不同的用户友好消息
        if "timeout" in error_msg.lower():
            user_msg = "请求超时，请稍后重试"
        elif "connection" in error_msg.lower():
            user_msg = "网络连接失败，请检查网络连接"
        elif "unauthorized" in error_msg.lower():
            user_msg = "API认证失败，请联系管理员"
        elif "not found" in error_msg.lower():
            user_msg = "请求的资源不存在"
        elif "json" in error_msg.lower():
            user_msg = "数据格式错误，请重试"
        else:
            user_msg = "服务暂时不可用，请稍后重试"
        
        return {
            'success': False,
            'error': user_msg,
            'error_code': 'API_ERROR',
            'debug_info': error_msg if settings.DEBUG else None
        }
    
    @staticmethod
    def handle_validation_error(error, field_name=None):
        """处理验证错误"""
        error_msg = str(error)
        logger.warning(f"验证错误: {error_msg}")
        
        if field_name:
            user_msg = f"{field_name}格式不正确: {error_msg}"
        else:
            user_msg = f"输入数据不正确: {error_msg}"
        
        return {
            'success': False,
            'error': user_msg,
            'error_code': 'VALIDATION_ERROR'
        }
    
    @staticmethod
    def handle_business_error(error, context="业务处理"):
        """处理业务逻辑错误"""
        error_msg = str(error)
        logger.warning(f"{context}错误: {error_msg}")
        
        return {
            'success': False,
            'error': error_msg,
            'error_code': 'BUSINESS_ERROR'
        }
    
    @staticmethod
    def handle_system_error(error, context="系统"):
        """处理系统错误"""
        error_msg = str(error)
        logger.error(f"{context}错误: {error_msg}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        # 系统错误不向用户暴露具体信息
        user_msg = "系统繁忙，请稍后重试"
        
        return {
            'success': False,
            'error': user_msg,
            'error_code': 'SYSTEM_ERROR',
            'debug_info': error_msg if settings.DEBUG else None
        }
    
    @staticmethod
    def create_success_response(data, message=None):
        """创建成功响应"""
        response = {
            'success': True,
            **data
        }
        
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def create_error_response(error_dict, status_code=400):
        """创建错误响应"""
        return JsonResponse(error_dict, status=status_code)

# 装饰器：统一错误处理
def handle_errors(context="操作"):
    """错误处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return ErrorHandler.handle_validation_error(e)
            except ConnectionError as e:
                return ErrorHandler.handle_api_error(e, context)
            except Exception as e:
                return ErrorHandler.handle_system_error(e, context)
        return wrapper
    return decorator

# 全局错误处理器实例
error_handler = ErrorHandler()
