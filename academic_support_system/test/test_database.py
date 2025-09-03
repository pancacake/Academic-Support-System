"""
数据库测试模块
测试数据库连接、模型和数据操作
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_django_setup():
    """测试Django设置"""
    try:
        import django
        from django.conf import settings
        
        if settings.configured:
            print("✅ Django设置测试成功")
            return True
        else:
            print("❌ Django设置测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Django设置测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ 数据库连接测试成功")
            return True
        else:
            print("❌ 数据库连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

def test_models_import():
    """测试模型导入"""
    try:
        from django.contrib.auth.models import User
        print("✅ 模型导入测试成功")
        return True
    except ImportError as e:
        print(f"❌ 模型导入测试失败: {e}")
        return False

def test_migrations():
    """测试迁移状态"""
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if not plan:
            print("✅ 迁移状态测试成功（无待执行迁移）")
            return True
        else:
            print(f"⚠️ 有 {len(plan)} 个待执行迁移")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ 迁移状态测试失败: {e}")
        return False

def run_tests():
    """运行所有数据库测试"""
    print("🔍 开始数据库测试...")
    
    tests = [
        ("Django设置", test_django_setup),
        ("数据库连接", test_database_connection),
        ("模型导入", test_models_import),
        ("迁移状态", test_migrations),
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
    
    print(f"\n📊 数据库测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
