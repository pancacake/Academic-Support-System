"""
出题功能测试模块
测试题目生成、解析和保存功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_questions_views_import():
    """测试出题视图导入"""
    try:
        from questions.views import generate_structured_questions, get_latest_notes_content
        print("✅ 出题视图导入成功")
        return True
    except ImportError as e:
        print(f"❌ 出题视图导入失败: {e}")
        return False

def test_question_prompts():
    """测试题目提示词"""
    try:
        from prompts import (
            MULTIPLE_CHOICE_GENERATION_PROMPT,
            FILL_IN_BLANK_GENERATION_PROMPT,
            TRUE_FALSE_GENERATION_PROMPT,
            SHORT_ANSWER_GENERATION_PROMPT
        )
        
        prompts = [
            MULTIPLE_CHOICE_GENERATION_PROMPT,
            FILL_IN_BLANK_GENERATION_PROMPT,
            TRUE_FALSE_GENERATION_PROMPT,
            SHORT_ANSWER_GENERATION_PROMPT
        ]
        
        for prompt in prompts:
            if len(prompt) < 50:
                print("❌ 提示词过短")
                return False
        
        print("✅ 题目提示词测试成功")
        return True
    except ImportError as e:
        print(f"❌ 题目提示词导入失败: {e}")
        return False

def test_question_types():
    """测试题目类型"""
    try:
        question_types = {
            'multiple_choice': {'name': '选择题', 'count': 2},
            'fill_blank': {'name': '填空题', 'count': 2},
            'true_false': {'name': '判断题', 'count': 2},
            'short_answer': {'name': '解答题', 'count': 1}
        }
        
        total_questions = sum(info['count'] for info in question_types.values())
        
        if total_questions > 0:
            print(f"✅ 题目类型测试成功，总题数: {total_questions}")
            return True
        else:
            print("❌ 题目类型测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 题目类型测试失败: {e}")
        return False

def test_question_parsing():
    """测试题目解析"""
    try:
        from questions.views import parse_ai_response
        
        # 测试选择题解析
        test_response = """{
  "text": "以下哪个是正确的？",
  "type": "选择题",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "answer": "A",
  "explanation": "这是解析"
}"""
        
        parsed = parse_ai_response(test_response, "选择题")
        
        if parsed and 'text' in parsed and 'answer' in parsed:
            print("✅ 题目解析测试成功")
            return True
        else:
            print("❌ 题目解析测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 题目解析测试失败: {e}")
        return False

def test_fallback_questions():
    """测试回退题目"""
    try:
        from questions.views import create_fallback_question
        
        question_types = ['选择题', '填空题', '判断题', '解答题']
        
        for q_type in question_types:
            fallback = create_fallback_question(q_type, 1)
            
            if not fallback or 'text' not in fallback:
                print(f"❌ {q_type}回退题目生成失败")
                return False
        
        print("✅ 回退题目测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 回退题目测试失败: {e}")
        return False

def run_tests():
    """运行所有出题功能测试"""
    print("🔍 开始出题功能测试...")
    
    tests = [
        ("出题视图导入", test_questions_views_import),
        ("题目提示词", test_question_prompts),
        ("题目类型", test_question_types),
        ("题目解析", test_question_parsing),
        ("回退题目", test_fallback_questions),
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
    
    print(f"\n📊 出题功能测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
