import json
import os
import re
import time
from typing import List, Dict, Any
import requests
from django.conf import settings

# 动态导入配置
import importlib.util
config_path = os.path.join(settings.BASE_DIR.parent, 'config.py')
spec = importlib.util.spec_from_file_location('config', config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

def get_latest_notes_content(user_id):
    """获取用户最新的笔记内容"""
    try:
        from .views import get_user_output_path
        output_dir = get_user_output_path(user_id)
        
        if not os.path.exists(output_dir):
            return None
            
        # 获取最新的笔记文件
        folders = []
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path):
                notes_file = os.path.join(item_path, 'notes.md')
                if os.path.exists(notes_file):
                    folders.append({
                        'path': notes_file,
                        'created': os.path.getctime(item_path)
                    })
        
        if not folders:
            return None
            
        # 获取最新的笔记文件
        latest_folder = max(folders, key=lambda x: x['created'])
        
        with open(latest_folder['path'], 'r', encoding='utf-8') as f:
            return f.read()
            
    except Exception as e:
        print(f"获取笔记内容失败: {e}")
        return None

def extract_topic_content(content, topic):
    """从笔记中提取与特定主题相关的内容"""
    lines = content.split('\n')
    relevant_lines = []

    # 查找包含主题关键词的段落
    for i, line in enumerate(lines):
        if topic.lower() in line.lower():
            # 添加前后几行作为上下文
            start = max(0, i - 3)
            end = min(len(lines), i + 10)
            relevant_lines.extend(lines[start:end])
            relevant_lines.append('\n---\n')  # 分隔符

    return '\n'.join(relevant_lines) if relevant_lines else None

def parse_user_requirement(requirement):
    """解析用户需求，提取题目数量、难度、主题等信息"""
    parsed = {
        'count': 5,  # 默认5道题
        'difficulty': '中等',  # 默认中等难度
        'topics': [],  # 特定主题
        'question_types': []  # 题目类型
    }

    # 提取题目数量
    count_match = re.search(r'(\d+)\s*[道题]', requirement)
    if count_match:
        parsed['count'] = min(int(count_match.group(1)), 20)  # 最多20道题

    # 提取难度
    if '简单' in requirement or '容易' in requirement or '基础' in requirement:
        parsed['difficulty'] = '简单'
    elif '困难' in requirement or '难' in requirement or '高级' in requirement or '深入' in requirement:
        parsed['difficulty'] = '困难'
    elif '中等' in requirement or '中级' in requirement:
        parsed['difficulty'] = '中等'

    # 提取题目类型
    if '选择题' in requirement:
        parsed['question_types'].append('选择题')
    if '填空题' in requirement:
        parsed['question_types'].append('填空题')
    if '判断题' in requirement:
        parsed['question_types'].append('判断题')
    if '简答题' in requirement:
        parsed['question_types'].append('简答题')

    # 如果没有指定类型，默认混合
    if not parsed['question_types']:
        parsed['question_types'] = ['选择题', '填空题']

    # 提取主题关键词
    topic_keywords = re.findall(r'关于(.+?)的', requirement)
    if topic_keywords:
        parsed['topics'].extend(topic_keywords)

    return parsed

def generate_questions_from_notes(user_id, requirement, question_types=None):
    """根据笔记内容生成题目"""
    try:
        # 获取笔记内容
        notes_content = get_latest_notes_content(user_id)
        if not notes_content:
            return {"success": False, "error": "没有找到笔记内容"}

        # 解析用户需求
        parsed_req = parse_user_requirement(requirement)

        # 如果传入了question_types，使用传入的类型
        if question_types:
            parsed_req['question_types'] = question_types

        # 根据主题筛选相关内容
        relevant_content = notes_content
        if parsed_req['topics']:
            # 简单的主题匹配，可以进一步优化
            topic_sections = []
            for topic in parsed_req['topics']:
                topic_content = extract_topic_content(notes_content, topic)
                if topic_content:
                    topic_sections.append(topic_content)
            if topic_sections:
                relevant_content = '\n\n'.join(topic_sections)

        # 限制内容长度
        if len(relevant_content) > 4000:
            relevant_content = relevant_content[:4000] + "..."

        # 构建更智能的提示词
        difficulty_desc = {
            '简单': '基础概念理解，适合初学者',
            '中等': '概念应用和分析，适合有一定基础的学习者',
            '困难': '深入分析和综合应用，适合高级学习者'
        }

        prompt = f"""
基于以下学习笔记内容，根据用户需求生成高质量的练习题目。

笔记内容：
{relevant_content}

用户需求分析：
- 题目数量：{parsed_req['count']}道
- 难度等级：{parsed_req['difficulty']} ({difficulty_desc.get(parsed_req['difficulty'], '')})
- 题目类型：{', '.join(parsed_req['question_types'])}
- 关注主题：{', '.join(parsed_req['topics']) if parsed_req['topics'] else '全部内容'}

请严格按照以下JSON格式返回题目：
{{
    "questions": [
        {{
            "type": "选择题",
            "text": "题目内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "A",
            "explanation": "详细解析，说明为什么这个答案正确"
        }},
        {{
            "type": "填空题",
            "text": "题目内容，用______表示填空位置",
            "answer": "正确答案",
            "explanation": "详细解析"
        }},
        {{
            "type": "判断题",
            "text": "判断题目内容",
            "answer": "正确/错误",
            "explanation": "详细解析"
        }},
        {{
            "type": "简答题",
            "text": "简答题目内容",
            "answer": "参考答案要点",
            "explanation": "答题要点和评分标准"
        }}
    ]
}}

生成要求：
1. 题目必须基于提供的笔记内容，不能脱离材料
2. 题目难度要符合指定的{parsed_req['difficulty']}级别
3. 每道题都要有详细的解析说明
4. 选择题必须有4个选项，其中只有1个正确答案
5. 填空题用______表示填空，答案要准确简洁
6. 判断题答案只能是"正确"或"错误"
7. 简答题要提供完整的参考答案要点
8. 总共生成{parsed_req['count']}道题目，类型分布要均匀
9. 确保返回的是有效的JSON格式
"""

        # 调用AI生成题目
        headers = {
            'Authorization': f'Bearer {config.API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': config.DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        response = requests.post(
            f'{config.BASE_URL}/chat/completions',
            headers=headers,
            json=data,
            timeout=120  # 增加到2分钟
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 解析JSON响应
            try:
                # 提取JSON部分
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # 如果没有代码块，尝试直接解析
                    json_str = content
                
                questions_data = json.loads(json_str)
                
                # 为每个题目添加ID
                for i, question in enumerate(questions_data.get('questions', [])):
                    question['id'] = f"q_{user_id}_{int(time.time())}_{i}"
                
                return {
                    "success": True,
                    "questions": questions_data.get('questions', [])
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始内容: {content}")
                return {"success": False, "error": "AI响应格式错误"}
                
        else:
            return {"success": False, "error": f"AI服务错误: {response.status_code}"}
            
    except Exception as e:
        print(f"生成题目失败: {e}")
        return {"success": False, "error": str(e)}

def check_answer_correctness(user_answer, correct_answer, question_type="选择题"):
    """检查答案正确性"""
    try:
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        if question_type == "选择题":
            # 对于选择题，只比较选项字母
            user_option = re.search(r'^([abcd])', user_answer)
            correct_option = re.search(r'^([abcd])', correct_answer)
            
            if user_option and correct_option:
                return user_option.group(1) == correct_option.group(1)
            else:
                return user_answer == correct_answer
        else:
            # 对于其他题型，进行模糊匹配
            return user_answer == correct_answer or user_answer in correct_answer
            
    except Exception as e:
        print(f"检查答案失败: {e}")
        return False
