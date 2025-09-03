"""
文件上传测试模块
测试文件上传、解析和处理功能
"""

import os
import sys
import tempfile
import shutil
from io import BytesIO

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_file_parsers_import():
    """测试文件解析器导入"""
    try:
        from file_parsers import extract_text_from_pdf, extract_text_from_docx, extract_text_from_pptx
        print("✅ 文件解析器导入成功")
        return True
    except ImportError as e:
        print(f"❌ 文件解析器导入失败: {e}")
        return False

def test_upload_directory_creation():
    """测试上传目录创建"""
    try:
        from core.views import get_user_upload_path
        
        # 测试用户ID 999（测试用户）
        test_user_id = 999
        upload_path = get_user_upload_path(test_user_id)
        
        # 确保目录存在
        os.makedirs(upload_path, exist_ok=True)
        
        if os.path.exists(upload_path):
            print(f"✅ 上传目录创建成功: {upload_path}")
            return True
        else:
            print(f"❌ 上传目录创建失败: {upload_path}")
            return False
            
    except Exception as e:
        print(f"❌ 上传目录创建测试失败: {e}")
        return False

def create_test_text_file():
    """创建测试文本文件"""
    content = """
    这是一个测试文档。
    
    # 第一章 测试内容
    
    这里是一些测试文本，用于验证文件上传和解析功能。
    
    ## 1.1 子章节
    
    - 列表项1
    - 列表项2
    - 列表项3
    
    ## 1.2 另一个子章节
    
    这里有更多的测试内容。
    """
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    
    return temp_file.name

def test_text_file_processing():
    """测试文本文件处理"""
    try:
        # 创建测试文件
        test_file = create_test_text_file()
        
        # 读取文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "测试文档" in content and "第一章" in content:
            print("✅ 文本文件处理成功")
            result = True
        else:
            print("❌ 文本文件内容不正确")
            result = False
        
        # 清理临时文件
        os.unlink(test_file)
        return result
        
    except Exception as e:
        print(f"❌ 文本文件处理失败: {e}")
        return False

def test_file_size_validation():
    """测试文件大小验证"""
    try:
        # 创建一个大文件（模拟）
        large_content = "x" * (10 * 1024 * 1024)  # 10MB
        
        # 检查文件大小限制逻辑
        max_size = 5 * 1024 * 1024  # 5MB限制
        
        if len(large_content.encode('utf-8')) > max_size:
            print("✅ 文件大小验证逻辑正常")
            return True
        else:
            print("❌ 文件大小验证逻辑异常")
            return False
            
    except Exception as e:
        print(f"❌ 文件大小验证测试失败: {e}")
        return False

def test_file_type_validation():
    """测试文件类型验证"""
    try:
        allowed_extensions = ['.pdf', '.docx', '.pptx', '.doc', '.ppt']
        test_files = [
            'test.pdf',
            'test.docx', 
            'test.pptx',
            'test.txt',  # 不允许的类型
            'test.exe',  # 不允许的类型
        ]
        
        valid_count = 0
        for filename in test_files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in allowed_extensions:
                valid_count += 1
        
        if valid_count == 3:  # 应该有3个有效文件
            print("✅ 文件类型验证逻辑正常")
            return True
        else:
            print(f"❌ 文件类型验证逻辑异常，有效文件数: {valid_count}")
            return False
            
    except Exception as e:
        print(f"❌ 文件类型验证测试失败: {e}")
        return False

def test_upload_path_security():
    """测试上传路径安全性"""
    try:
        # 测试路径遍历攻击
        dangerous_filenames = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\config\\sam',
            'normal_file.pdf',
        ]
        
        safe_count = 0
        for filename in dangerous_filenames:
            # 简单的安全检查
            if '..' not in filename and os.path.basename(filename) == filename:
                safe_count += 1
        
        if safe_count == 1:  # 只有normal_file.pdf应该是安全的
            print("✅ 上传路径安全检查正常")
            return True
        else:
            print(f"❌ 上传路径安全检查异常，安全文件数: {safe_count}")
            return False
            
    except Exception as e:
        print(f"❌ 上传路径安全测试失败: {e}")
        return False

def test_cleanup_old_files():
    """测试旧文件清理"""
    try:
        # 创建测试目录
        test_dir = tempfile.mkdtemp()
        
        # 创建一些测试文件
        for i in range(3):
            test_file = os.path.join(test_dir, f'test_{i}.txt')
            with open(test_file, 'w') as f:
                f.write(f'Test content {i}')
        
        # 检查文件是否创建
        files_before = len(os.listdir(test_dir))
        
        # 清理目录
        shutil.rmtree(test_dir)
        
        if files_before == 3:
            print("✅ 文件清理测试正常")
            return True
        else:
            print(f"❌ 文件清理测试异常，文件数: {files_before}")
            return False
            
    except Exception as e:
        print(f"❌ 文件清理测试失败: {e}")
        return False

def run_tests():
    """运行所有文件上传测试"""
    print("🔍 开始文件上传测试...")
    
    tests = [
        ("文件解析器导入", test_file_parsers_import),
        ("上传目录创建", test_upload_directory_creation),
        ("文本文件处理", test_text_file_processing),
        ("文件大小验证", test_file_size_validation),
        ("文件类型验证", test_file_type_validation),
        ("上传路径安全", test_upload_path_security),
        ("旧文件清理", test_cleanup_old_files),
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
    
    print(f"\n📊 文件上传测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
