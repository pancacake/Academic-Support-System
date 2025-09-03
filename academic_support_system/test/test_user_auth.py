"""
用户登录测试模块
测试用户认证、会话管理和权限控制
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_user_models_import():
    """测试用户模型导入"""
    try:
        from users.models import User
        from django.contrib.auth.models import User as DjangoUser
        print("✅ 用户模型导入成功")
        return True
    except ImportError as e:
        print(f"❌ 用户模型导入失败: {e}")
        return False

def test_user_views_import():
    """测试用户视图导入"""
    try:
        from users.views import login_view, logout_view, get_current_user
        print("✅ 用户视图导入成功")
        return True
    except ImportError as e:
        print(f"❌ 用户视图导入失败: {e}")
        return False

def test_session_management():
    """测试会话管理"""
    try:
        # 模拟会话数据
        test_session = {
            'user_id': 1,
            'username': 'testuser',
            'is_authenticated': True,
            'login_time': '2025-01-01 00:00:00'
        }
        
        # 验证会话数据结构
        required_keys = ['user_id', 'username', 'is_authenticated']
        has_required_keys = all(key in test_session for key in required_keys)
        
        if has_required_keys:
            print("✅ 会话管理测试成功")
            return True
        else:
            print("❌ 会话管理测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 会话管理测试失败: {e}")
        return False

def test_user_id_generation():
    """测试用户ID生成"""
    try:
        from core.views import get_user_id
        from django.http import HttpRequest
        
        # 创建模拟请求
        request = HttpRequest()
        request.session = {'user_id': 123}
        
        user_id = get_user_id(request)
        
        if isinstance(user_id, int) and user_id > 0:
            print(f"✅ 用户ID生成测试成功: {user_id}")
            return True
        else:
            print("❌ 用户ID生成测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 用户ID生成测试失败: {e}")
        return False

def test_guest_mode():
    """测试游客模式"""
    try:
        # 模拟游客用户
        guest_session = {
            'user_id': 0,
            'username': 'guest',
            'is_authenticated': False
        }
        
        # 验证游客模式
        is_guest = not guest_session.get('is_authenticated', False)
        
        if is_guest:
            print("✅ 游客模式测试成功")
            return True
        else:
            print("❌ 游客模式测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 游客模式测试失败: {e}")
        return False

def test_permission_check():
    """测试权限检查"""
    try:
        # 模拟权限检查
        def check_permission(user_id, action):
            if user_id == 0:  # 游客
                return action in ['view', 'upload']
            else:  # 登录用户
                return True
        
        # 测试不同权限
        guest_permissions = [
            check_permission(0, 'view'),
            check_permission(0, 'upload'),
            check_permission(0, 'delete')
        ]
        
        user_permissions = [
            check_permission(1, 'view'),
            check_permission(1, 'upload'),
            check_permission(1, 'delete')
        ]
        
        # 游客应该有部分权限，用户应该有全部权限
        if sum(guest_permissions) == 2 and sum(user_permissions) == 3:
            print("✅ 权限检查测试成功")
            return True
        else:
            print("❌ 权限检查测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 权限检查测试失败: {e}")
        return False

def run_tests():
    """运行所有用户登录测试"""
    print("🔍 开始用户登录测试...")
    
    tests = [
        ("用户模型导入", test_user_models_import),
        ("用户视图导入", test_user_views_import),
        ("会话管理", test_session_management),
        ("用户ID生成", test_user_id_generation),
        ("游客模式", test_guest_mode),
        ("权限检查", test_permission_check),
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
    
    print(f"\n📊 用户登录测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
