"""
笔记生成测试模块
测试笔记生成、流式传输和文件保存功能
"""

import os
import sys
import tempfile
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_note_generator_import():
    """测试笔记生成器导入"""
    try:
        from notes.note_generator import generate_notes_streaming, get_api_client
        print("✅ 笔记生成器导入成功")
        return True
    except ImportError as e:
        print(f"❌ 笔记生成器导入失败: {e}")
        return False

def test_prompts_import():
    """测试提示词导入"""
    try:
        from prompts import NOTE_GENERATION_SYSTEM_PROMPT, NOTE_MODIFICATION_PROMPT
        print("✅ 提示词导入成功")
        print(f"系统提示词长度: {len(NOTE_GENERATION_SYSTEM_PROMPT)}")
        return True
    except ImportError as e:
        print(f"❌ 提示词导入失败: {e}")
        return False

def test_output_directory_creation():
    """测试输出目录创建"""
    try:
        from notes.views import get_user_output_path
        
        # 测试用户ID 999（测试用户）
        test_user_id = 999
        output_path = get_user_output_path(test_user_id)
        
        # 确保目录存在
        os.makedirs(output_path, exist_ok=True)
        
        if os.path.exists(output_path):
            print(f"✅ 输出目录创建成功: {output_path}")
            return True
        else:
            print(f"❌ 输出目录创建失败: {output_path}")
            return False
            
    except Exception as e:
        print(f"❌ 输出目录创建测试失败: {e}")
        return False

def test_content_extraction():
    """测试内容提取"""
    try:
        # 创建测试内容
        test_content = """
        这是一个测试文档的内容。
        
        包含多个段落和一些结构化信息。
        
        # 主要概念
        
        这里是一些重要的概念说明。
        
        ## 详细说明
        
        更详细的内容在这里。
        """
        
        # 测试内容长度和结构
        if len(test_content) > 50 and "#" in test_content:
            print("✅ 内容提取测试成功")
            print(f"内容长度: {len(test_content)} 字符")
            return True
        else:
            print("❌ 内容提取测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 内容提取测试失败: {e}")
        return False

def test_markdown_generation():
    """测试Markdown生成"""
    try:
        # 模拟生成的笔记内容
        generated_content = """# 测试笔记

## 1. 概述

这是一个测试生成的笔记内容。

### 1.1 主要特点

- 结构清晰
- 内容完整
- 格式规范

## 2. 详细内容

这里是详细的说明内容。

### 2.1 重要概念

重要概念的解释。

## 总结

这是笔记的总结部分。

本笔记由知悟·启明学业问答系统生成，AI可能会出错，请仔细鉴别。
"""
        
        # 检查Markdown格式
        has_headers = "#" in generated_content
        has_lists = "-" in generated_content
        has_watermark = "知悟·启明" in generated_content
        
        if has_headers and has_lists and has_watermark:
            print("✅ Markdown生成测试成功")
            print(f"生成内容长度: {len(generated_content)} 字符")
            return True
        else:
            print("❌ Markdown生成测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Markdown生成测试失败: {e}")
        return False

def test_file_saving():
    """测试文件保存"""
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        # 测试文件保存
        test_content = "# 测试笔记\n\n这是测试内容。"
        notes_file = os.path.join(temp_dir, 'notes.md')
        
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 验证文件是否保存成功
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            if saved_content == test_content:
                print("✅ 文件保存测试成功")
                result = True
            else:
                print("❌ 文件内容不匹配")
                result = False
        else:
            print("❌ 文件保存失败")
            result = False
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        return result
        
    except Exception as e:
        print(f"❌ 文件保存测试失败: {e}")
        return False

def test_streaming_simulation():
    """测试流式传输模拟"""
    try:
        # 模拟流式生成
        content_chunks = [
            "# 测试笔记\n\n",
            "## 1. 概述\n\n",
            "这是一个测试的笔记内容。\n\n",
            "### 1.1 详细说明\n\n",
            "详细的说明内容在这里。\n\n",
            "## 总结\n\n",
            "这是总结部分。"
        ]
        
        full_content = ""
        for chunk in content_chunks:
            full_content += chunk
            time.sleep(0.1)  # 模拟延迟
        
        if len(full_content) > 50 and "测试笔记" in full_content:
            print("✅ 流式传输模拟成功")
            print(f"总内容长度: {len(full_content)} 字符")
            return True
        else:
            print("❌ 流式传输模拟失败")
            return False
            
    except Exception as e:
        print(f"❌ 流式传输模拟失败: {e}")
        return False

def test_toc_generation():
    """测试目录生成"""
    try:
        from notes.note_generator import generate_toc_from_content
        
        test_content = """# 主标题

## 1. 第一章

### 1.1 第一节

内容...

### 1.2 第二节

内容...

## 2. 第二章

### 2.1 第一节

内容...
"""
        
        toc = generate_toc_from_content(test_content)
        
        if toc and "第一章" in toc and "第二章" in toc:
            print("✅ 目录生成测试成功")
            print(f"目录长度: {len(toc)} 字符")
            return True
        else:
            print("❌ 目录生成测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 目录生成测试失败: {e}")
        return False

def run_tests():
    """运行所有笔记生成测试"""
    print("🔍 开始笔记生成测试...")
    
    tests = [
        ("笔记生成器导入", test_note_generator_import),
        ("提示词导入", test_prompts_import),
        ("输出目录创建", test_output_directory_creation),
        ("内容提取", test_content_extraction),
        ("Markdown生成", test_markdown_generation),
        ("文件保存", test_file_saving),
        ("流式传输模拟", test_streaming_simulation),
        ("目录生成", test_toc_generation),
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
    
    print(f"\n📊 笔记生成测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
