"""
学术支持系统测试包
Academic Support System Test Package

这个包包含了系统的所有测试模块，提供全面的测试覆盖。

测试模块：
- test_api_client: API客户端测试
- test_file_upload: 文件上传测试
- test_note_generation: 笔记生成测试
- test_mindmap: 思维导图测试
- test_questions: 出题功能测试
- test_user_auth: 用户认证测试
- test_chat: 聊天功能测试
- test_database: 数据库测试
- test_frontend: 前端功能测试
- test_performance: 性能测试
- test_integration: 集成测试

使用方法：
1. 运行单个测试模块：
   python test/test_api_client.py

2. 运行所有测试：
   python test/test_runner.py

3. 交互式测试：
   python test/test_runner.py
   然后选择要运行的测试模块
"""

__version__ = "1.0.0"
__author__ = "Academic Support System Team"

# 测试模块列表
TEST_MODULES = [
    'test_api_client',
    'test_file_upload', 
    'test_note_generation',
    'test_mindmap',
    'test_questions',
    'test_user_auth',
    'test_chat',
    'test_database',
    'test_frontend',
    'test_performance',
    'test_integration'
]

def run_all_tests():
    """运行所有测试模块"""
    from .test_runner import TestRunner
    runner = TestRunner()
    return runner.run_all_tests()
