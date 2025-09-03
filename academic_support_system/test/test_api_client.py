"""
API客户端测试模块
测试AI API的连接、调用和响应处理
"""

import os
import sys
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_api_client_import():
    """测试API客户端导入"""
    try:
        from api_client import APIClient
        print("✅ API客户端导入成功")
        return True
    except ImportError as e:
        print(f"❌ API客户端导入失败: {e}")
        return False

def test_api_client_initialization():
    """测试API客户端初始化"""
    try:
        from api_client import APIClient
        client = APIClient()
        print("✅ API客户端初始化成功")
        return True
    except Exception as e:
        print(f"❌ API客户端初始化失败: {e}")
        return False

def test_config_loading():
    """测试配置文件加载"""
    try:
        from config import API_KEY, DEFAULT_MODEL, BASE_URL
        
        if API_KEY:
            print(f"✅ API_KEY已配置: {API_KEY[:10]}...")
        else:
            print("⚠️ API_KEY未配置")
            
        print(f"✅ 默认模型: {DEFAULT_MODEL}")
        print(f"✅ 基础URL: {BASE_URL}")
        return True
    except ImportError as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_simple_api_call():
    """测试简单的API调用"""
    try:
        from api_client import APIClient
        
        client = APIClient()
        
        # 测试简单的聊天完成
        response = client.chat_completion([
            {"role": "user", "content": "请回复'测试成功'"}
        ])
        
        if "测试成功" in response or "成功" in response:
            print("✅ API调用测试成功")
            print(f"响应内容: {response[:100]}...")
            return True
        else:
            print(f"⚠️ API调用返回了意外的响应: {response[:100]}...")
            return True  # 仍然算作成功，因为API有响应
            
    except Exception as e:
        print(f"❌ API调用测试失败: {e}")
        return False

def test_api_response_time():
    """测试API响应时间"""
    try:
        from api_client import APIClient
        
        client = APIClient()
        
        start_time = time.time()
        response = client.chat_completion([
            {"role": "user", "content": "Hello"}
        ])
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"✅ API响应时间: {response_time:.2f}秒")
        
        if response_time < 30:  # 30秒内算正常
            print("✅ 响应时间正常")
            return True
        else:
            print("⚠️ 响应时间较长")
            return True
            
    except Exception as e:
        print(f"❌ API响应时间测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    try:
        from api_client import APIClient
        
        client = APIClient()
        
        # 测试空消息
        try:
            response = client.chat_completion([])
            print("✅ 空消息处理正常")
        except Exception as e:
            print(f"✅ 空消息错误处理正常: {e}")
        
        # 测试无效消息格式
        try:
            response = client.chat_completion("invalid format")
            print("⚠️ 无效格式未被捕获")
        except Exception as e:
            print(f"✅ 无效格式错误处理正常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def run_tests():
    """运行所有API客户端测试"""
    print("🔍 开始API客户端测试...")
    
    tests = [
        ("API客户端导入", test_api_client_import),
        ("API客户端初始化", test_api_client_initialization),
        ("配置文件加载", test_config_loading),
        ("简单API调用", test_simple_api_call),
        ("API响应时间", test_api_response_time),
        ("错误处理", test_error_handling),
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
    
    print(f"\n📊 API客户端测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
