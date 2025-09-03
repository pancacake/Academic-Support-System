#!/usr/bin/env python
"""
学术支持系统 - 综合测试运行器
Academic Support System - Comprehensive Test Runner

这个脚本提供了一个交互式的测试界面，允许用户选择要测试的模块和功能。
"""

import os
import sys
import importlib
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_support_system.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Django初始化失败: {e}")

class TestRunner:
    def __init__(self):
        self.test_modules = {
            '1': ('API客户端测试', 'test_api_client'),
            '2': ('文件上传测试', 'test_file_upload'),
            '3': ('笔记生成测试', 'test_note_generation'),
            '4': ('思维导图测试', 'test_mindmap'),
            '5': ('出题功能测试', 'test_questions'),
            '6': ('用户登录测试', 'test_user_auth'),
            '7': ('聊天功能测试', 'test_chat'),
            '8': ('数据库测试', 'test_database'),
            '9': ('前端功能测试', 'test_frontend'),
            '10': ('性能测试', 'test_performance'),
            '11': ('集成测试', 'test_integration'),
            '0': ('运行所有测试', 'run_all_tests')
        }
    
    def display_menu(self):
        """显示测试菜单"""
        print("\n" + "="*60)
        print("🧪 学术支持系统 - 测试运行器")
        print("="*60)
        print("请选择要运行的测试模块：")
        print()
        
        for key, (name, _) in self.test_modules.items():
            if key == '0':
                print(f"  {key}. 🚀 {name}")
            else:
                print(f"  {key}. {name}")
        
        print()
        print("  q. 退出")
        print("="*60)
    
    def run_test_module(self, module_name):
        """运行指定的测试模块"""
        try:
            print(f"\n🔍 正在运行测试模块: {module_name}")
            print("-" * 50)
            
            # 动态导入测试模块
            test_module = importlib.import_module(f'test.{module_name}')
            
            # 查找并运行测试函数
            if hasattr(test_module, 'run_tests'):
                result = test_module.run_tests()
                return result
            else:
                print(f"❌ 测试模块 {module_name} 没有 run_tests 函数")
                return False
                
        except ImportError as e:
            print(f"❌ 无法导入测试模块 {module_name}: {e}")
            return False
        except Exception as e:
            print(f"❌ 运行测试时出错: {e}")
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始运行所有测试...")
        print("="*60)
        
        results = {}
        total_tests = len(self.test_modules) - 1  # 排除"运行所有测试"选项
        
        for key, (name, module_name) in self.test_modules.items():
            if key == '0':  # 跳过"运行所有测试"选项
                continue
                
            print(f"\n📋 测试进度: {len(results) + 1}/{total_tests}")
            result = self.run_test_module(module_name)
            results[name] = result
        
        # 显示测试总结
        self.display_test_summary(results)
        return results
    
    def display_test_summary(self, results):
        """显示测试总结"""
        print("\n" + "="*60)
        print("📊 测试总结报告")
        print("="*60)
        
        passed = sum(1 for result in results.values() if result)
        failed = len(results) - passed
        
        print(f"总测试数: {len(results)}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"成功率: {passed/len(results)*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
        
        print("="*60)
        print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run(self):
        """运行测试器主循环"""
        print("欢迎使用学术支持系统测试运行器！")
        
        while True:
            self.display_menu()
            choice = input("\n请输入选择: ").strip()
            
            if choice.lower() == 'q':
                print("👋 感谢使用测试运行器，再见！")
                break
            
            if choice in self.test_modules:
                name, module_name = self.test_modules[choice]
                
                if choice == '0':
                    self.run_all_tests()
                else:
                    result = self.run_test_module(module_name)
                    if result:
                        print(f"\n✅ {name} 测试通过！")
                    else:
                        print(f"\n❌ {name} 测试失败！")
                
                input("\n按回车键继续...")
            else:
                print("❌ 无效选择，请重新输入！")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
