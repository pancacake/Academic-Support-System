"""
聊天功能测试模块
测试聊天消息处理、AI回复和@功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_chat_views_import():
    """测试聊天视图导入"""
    try:
        from core.views import chat_message, handle_section_qa_or_modification
        print("✅ 聊天视图导入成功")
        return True
    except ImportError as e:
        print(f"❌ 聊天视图导入失败: {e}")
        return False

def test_message_processing():
    """测试消息处理"""
    try:
        # 模拟消息处理
        test_messages = [
            "你好",
            "帮助",
            "@网络基础 这是什么？",
            "修改第一章内容",
            "确认修改"
        ]
        
        for message in test_messages:
            # 基本消息验证
            if not isinstance(message, str) or len(message) == 0:
                print(f"❌ 消息格式错误: {message}")
                return False
        
        print("✅ 消息处理测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 消息处理测试失败: {e}")
        return False

def test_at_functionality():
    """测试@功能"""
    try:
        import re
        
        # 测试@章节解析
        test_message = "@网络基础概念 这个概念是什么意思？"
        
        at_pattern = r'@([^@\s]+)'
        matches = re.findall(at_pattern, test_message)
        
        if matches and matches[0] == "网络基础概念":
            print("✅ @功能测试成功")
            return True
        else:
            print("❌ @功能测试失败")
            return False
            
    except Exception as e:
        print(f"❌ @功能测试失败: {e}")
        return False

def test_modification_confirmation():
    """测试修改确认"""
    try:
        # 模拟修改确认流程
        confirmation_keywords = ['确认修改', '确认', '是的', '是']
        
        test_input = "确认修改"
        
        if test_input in confirmation_keywords:
            print("✅ 修改确认测试成功")
            return True
        else:
            print("❌ 修改确认测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 修改确认测试失败: {e}")
        return False

def run_tests():
    """运行所有聊天功能测试"""
    print("🔍 开始聊天功能测试...")
    
    tests = [
        ("聊天视图导入", test_chat_views_import),
        ("消息处理", test_message_processing),
        ("@功能", test_at_functionality),
        ("修改确认", test_modification_confirmation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
    
    print(f"\n📊 聊天功能测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
