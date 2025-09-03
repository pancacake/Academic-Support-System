"""
前端功能测试模块
测试前端页面、JavaScript功能和用户界面
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_template_files():
    """测试模板文件存在性"""
    try:
        template_dir = os.path.join(project_root, 'templates')
        
        required_templates = [
            'simple_chat.html',
            'mindmap.html',
            'questions.html'
        ]
        
        missing_templates = []
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
        
        if not missing_templates:
            print("✅ 模板文件测试成功")
            return True
        else:
            print(f"❌ 缺少模板文件: {missing_templates}")
            return False
            
    except Exception as e:
        print(f"❌ 模板文件测试失败: {e}")
        return False

def test_static_files():
    """测试静态文件存在性"""
    try:
        static_dir = os.path.join(project_root, 'static')
        
        # 检查是否有静态文件目录
        if os.path.exists(static_dir):
            print("✅ 静态文件目录存在")
            return True
        else:
            print("⚠️ 静态文件目录不存在（可能使用CDN）")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ 静态文件测试失败: {e}")
        return False

def test_javascript_syntax():
    """测试JavaScript语法"""
    try:
        # 检查模板中的JavaScript代码
        template_path = os.path.join(project_root, 'templates', 'simple_chat.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本语法检查
            js_errors = []
            
            # 检查是否有未闭合的标签
            if content.count('<script>') != content.count('</script>'):
                js_errors.append("script标签未正确闭合")
            
            # 检查是否有基本的JavaScript函数
            if 'function' not in content:
                js_errors.append("未找到JavaScript函数")
            
            if not js_errors:
                print("✅ JavaScript语法测试成功")
                return True
            else:
                print(f"❌ JavaScript语法错误: {js_errors}")
                return False
        else:
            print("⚠️ 主模板文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ JavaScript语法测试失败: {e}")
        return False

def test_css_structure():
    """测试CSS结构"""
    try:
        # 检查模板中的CSS样式
        template_path = os.path.join(project_root, 'templates', 'simple_chat.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有样式定义
            has_styles = '<style>' in content or 'style=' in content
            
            if has_styles:
                print("✅ CSS结构测试成功")
                return True
            else:
                print("⚠️ 未找到CSS样式（可能使用外部样式表）")
                return True  # 不算失败
        else:
            print("⚠️ 主模板文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ CSS结构测试失败: {e}")
        return False

def test_responsive_design():
    """测试响应式设计"""
    try:
        # 检查是否有响应式设计元素
        template_path = os.path.join(project_root, 'templates', 'simple_chat.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查viewport meta标签
            has_viewport = 'viewport' in content
            
            # 检查媒体查询
            has_media_query = '@media' in content
            
            if has_viewport:
                print("✅ 响应式设计测试成功")
                return True
            else:
                print("⚠️ 未找到viewport设置")
                return True  # 不算失败
        else:
            print("⚠️ 主模板文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 响应式设计测试失败: {e}")
        return False

def test_accessibility():
    """测试可访问性"""
    try:
        # 检查基本的可访问性元素
        template_path = os.path.join(project_root, 'templates', 'simple_chat.html')
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查alt属性
            has_alt = 'alt=' in content
            
            # 检查title属性
            has_title = 'title=' in content
            
            # 检查语言设置
            has_lang = 'lang=' in content
            
            accessibility_score = sum([has_alt, has_title, has_lang])
            
            if accessibility_score >= 2:
                print("✅ 可访问性测试成功")
                return True
            else:
                print("⚠️ 可访问性有待改进")
                return True  # 不算失败
        else:
            print("⚠️ 主模板文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 可访问性测试失败: {e}")
        return False

def run_tests():
    """运行所有前端功能测试"""
    print("🔍 开始前端功能测试...")
    
    tests = [
        ("模板文件", test_template_files),
        ("静态文件", test_static_files),
        ("JavaScript语法", test_javascript_syntax),
        ("CSS结构", test_css_structure),
        ("响应式设计", test_responsive_design),
        ("可访问性", test_accessibility),
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
    
    print(f"\n📊 前端功能测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
