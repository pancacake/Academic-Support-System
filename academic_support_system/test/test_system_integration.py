#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知悟·启明学业问答系统 - 系统集成测试
测试整个系统的端到端功能，包括登录、文件上传、笔记生成、思维导图、出题等
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class SystemIntegrationTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.cookies = {}  # 简单的cookie存储
        
    def log_test(self, test_name, success, message="", details=None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"    详情: {details}")

    def make_request(self, url, method="GET", data=None, headers=None):
        """发送HTTP请求的辅助方法"""
        try:
            if headers is None:
                headers = {}

            if method == "GET":
                req = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(req, timeout=10)
                return {
                    'status_code': response.getcode(),
                    'text': response.read().decode('utf-8'),
                    'headers': dict(response.headers)
                }
            elif method == "POST":
                if data:
                    if isinstance(data, dict):
                        data = json.dumps(data).encode('utf-8')
                        headers['Content-Type'] = 'application/json'
                    elif isinstance(data, str):
                        data = data.encode('utf-8')

                req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                response = urllib.request.urlopen(req, timeout=10)
                return {
                    'status_code': response.getcode(),
                    'text': response.read().decode('utf-8'),
                    'headers': dict(response.headers)
                }
        except urllib.error.HTTPError as e:
            return {
                'status_code': e.code,
                'text': e.read().decode('utf-8') if hasattr(e, 'read') else str(e),
                'headers': {}
            }
        except Exception as e:
            return {
                'status_code': 0,
                'text': str(e),
                'headers': {}
            }
    
    def test_server_availability(self):
        """测试服务器可用性"""
        try:
            response = self.make_request(f"{self.base_url}/login/")
            if response['status_code'] == 200:
                self.log_test("服务器可用性", True, "服务器正常响应")
                return True
            else:
                self.log_test("服务器可用性", False, f"服务器响应异常: {response['status_code']}")
                return False
        except Exception as e:
            self.log_test("服务器可用性", False, f"无法连接到服务器: {str(e)}")
            return False
    
    def test_login_portal(self):
        """测试登录门户页面"""
        try:
            response = self.make_request(f"{self.base_url}/login/")
            if response['status_code'] == 200:
                content = response['text']
                required_elements = [
                    "知悟·启明",
                    "学业问答系统",
                    "用户名",
                    "密码",
                    "游客模式进入"
                ]

                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)

                if not missing_elements:
                    self.log_test("登录门户页面", True, "登录页面包含所有必要元素")
                    return True
                else:
                    self.log_test("登录门户页面", False, f"缺少元素: {missing_elements}")
                    return False
            else:
                self.log_test("登录门户页面", False, f"页面加载失败: {response['status_code']}")
                return False
        except Exception as e:
            self.log_test("登录门户页面", False, f"测试异常: {str(e)}")
            return False
    
    def test_guest_mode_entry(self):
        """测试游客模式进入"""
        try:
            # 获取CSRF token
            response = self.session.get(f"{self.base_url}/login/")
            csrf_token = self.extract_csrf_token(response.text)
            
            # 设置游客模式
            response = self.session.post(
                f"{self.base_url}/users/api/guest-mode/",
                headers={
                    'X-CSRFToken': csrf_token,
                    'Content-Type': 'application/json'
                },
                json={}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("游客模式进入", True, "成功进入游客模式")
                    return True
                else:
                    self.log_test("游客模式进入", False, f"API返回失败: {data}")
                    return False
            else:
                self.log_test("游客模式进入", False, f"请求失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("游客模式进入", False, f"测试异常: {str(e)}")
            return False
    
    def test_main_page_access(self):
        """测试主页面访问"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                content = response.text
                required_elements = [
                    "知悟·启明学业问答系统",
                    "上传文件",
                    "思维导图",
                    "出题"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_test("主页面访问", True, "主页面包含所有必要元素")
                    return True
                else:
                    self.log_test("主页面访问", False, f"缺少元素: {missing_elements}")
                    return False
            else:
                self.log_test("主页面访问", False, f"页面加载失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("主页面访问", False, f"测试异常: {str(e)}")
            return False
    
    def test_questions_page_access(self):
        """测试出题页面访问"""
        try:
            response = self.session.get(f"{self.base_url}/questions/")
            if response.status_code == 200:
                content = response.text
                required_elements = [
                    "智能出题系统",
                    "选择题",
                    "填空题",
                    "判断题",
                    "解答题"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_test("出题页面访问", True, "出题页面包含所有必要元素")
                    return True
                else:
                    self.log_test("出题页面访问", False, f"缺少元素: {missing_elements}")
                    return False
            else:
                self.log_test("出题页面访问", False, f"页面加载失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("出题页面访问", False, f"测试异常: {str(e)}")
            return False
    
    def test_mindmap_page_access(self):
        """测试思维导图页面访问"""
        try:
            response = self.session.get(f"{self.base_url}/mindmap/")
            if response.status_code == 200:
                content = response.text
                required_elements = [
                    "思维导图",
                    "AI增强",
                    "导出图片"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_test("思维导图页面访问", True, "思维导图页面包含所有必要元素")
                    return True
                else:
                    self.log_test("思维导图页面访问", False, f"缺少元素: {missing_elements}")
                    return False
            else:
                self.log_test("思维导图页面访问", False, f"页面加载失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("思维导图页面访问", False, f"测试异常: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """测试API端点"""
        try:
            # 获取CSRF token
            response = self.session.get(f"{self.base_url}/")
            csrf_token = self.extract_csrf_token(response.text)
            
            # 测试用户状态API
            response = self.session.get(f"{self.base_url}/users/api/current-user/")
            if response.status_code == 200:
                self.log_test("用户状态API", True, "API正常响应")
            else:
                self.log_test("用户状态API", False, f"API响应异常: {response.status_code}")
                return False
            
            # 测试文件列表API
            response = self.session.get(f"{self.base_url}/api/files/")
            if response.status_code == 200:
                self.log_test("文件列表API", True, "API正常响应")
            else:
                self.log_test("文件列表API", False, f"API响应异常: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("API端点测试", False, f"测试异常: {str(e)}")
            return False
    
    def test_theme_system(self):
        """测试主题系统"""
        try:
            response = self.session.get(f"{self.base_url}/")
            content = response.text
            
            # 检查CSS变量和主题相关代码
            theme_elements = [
                "--bg-primary",
                "--text-primary", 
                "data-theme",
                "toggleTheme"
            ]
            
            missing_elements = []
            for element in theme_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                self.log_test("主题系统", True, "主题系统代码完整")
                return True
            else:
                self.log_test("主题系统", False, f"缺少主题元素: {missing_elements}")
                return False
        except Exception as e:
            self.log_test("主题系统", False, f"测试异常: {str(e)}")
            return False
    
    def test_markdown_rendering(self):
        """测试Markdown渲染功能"""
        try:
            response = self.session.get(f"{self.base_url}/")
            content = response.text
            
            # 检查Markdown和数学公式相关代码
            markdown_elements = [
                "marked.min.js",
                "MathJax",
                "renderBasicMarkdown",
                "preprocessMath"
            ]
            
            missing_elements = []
            for element in markdown_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                self.log_test("Markdown渲染", True, "Markdown渲染功能完整")
                return True
            else:
                self.log_test("Markdown渲染", False, f"缺少Markdown元素: {missing_elements}")
                return False
        except Exception as e:
            self.log_test("Markdown渲染", False, f"测试异常: {str(e)}")
            return False
    
    def extract_csrf_token(self, html_content):
        """从HTML中提取CSRF token"""
        import re
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html_content)
        if match:
            return match.group(1)
        
        match = re.search(r'content="([^"]+)" name="csrf-token"', html_content)
        if match:
            return match.group(1)
        
        return None
    
    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = datetime.now()
        print("🚀 开始系统集成测试...")
        print("=" * 60)
        
        # 基础功能测试
        tests = [
            self.test_server_availability,
            self.test_login_portal,
            self.test_guest_mode_entry,
            self.test_main_page_access,
            self.test_questions_page_access,
            self.test_mindmap_page_access,
            self.test_api_endpoints,
            self.test_theme_system,
            self.test_markdown_rendering
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ 测试执行异常: {test.__name__} - {str(e)}")
                failed += 1
            
            time.sleep(0.5)  # 避免请求过快
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        print("=" * 60)
        print(f"📊 测试完成 - 耗时: {duration:.2f}秒")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
        
        return passed, failed, self.test_results

def main():
    """主函数"""
    print("知悟·启明学业问答系统 - 系统集成测试")
    print("=" * 60)
    
    tester = SystemIntegrationTest()
    passed, failed, results = tester.run_all_tests()
    
    # 保存测试结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'passed': passed,
                    'failed': failed,
                    'total': passed + failed,
                    'success_rate': passed/(passed+failed)*100 if (passed+failed) > 0 else 0,
                    'duration': (tester.end_time - tester.start_time).total_seconds(),
                    'timestamp': tester.start_time.isoformat()
                },
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到: {results_file}")
    except Exception as e:
        print(f"\n⚠️ 保存测试结果失败: {str(e)}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
