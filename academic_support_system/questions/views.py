from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import os
import sys
import logging
from datetime import datetime
from openai import OpenAI

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

# 导入统一的服务
from core.question_service import question_service
from core.unified_api_client import unified_client
from core.utils import get_user_id_from_request, get_user_latest_notes, save_generated_questions
from core.error_handler import error_handler

# 配置日志
logger = logging.getLogger(__name__)

def save_questions_to_file(questions, user_id):
    """保存题目到用户的notes目录"""
    try:
        from django.conf import settings

        # 创建用户的notes目录 - 按照新的逻辑
        user_notes_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), 'output', 'notes')
        os.makedirs(user_notes_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f'questions_{timestamp}.json'
        filepath = os.path.join(user_notes_dir, filename)

        # 保存题目数据
        questions_data = {
            'timestamp': timestamp,
            'user_id': user_id,
            'questions': questions,
            'total_count': len(questions),
            'generated_at': datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 题目已保存到用户notes目录: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"保存题目到文件失败: {e}")
        raise

def questions_page(request):
    """出题页面 - 允许直接访问"""
    # 自动设置游客模式以便测试
    if not request.user.is_authenticated:
        request.session['guest_mode'] = True

    return render(request, 'questions.html')

def questions_test_page(request):
    """出题测试页面 - 简化版"""
    return render(request, 'questions_simple.html')

@csrf_exempt
@require_http_methods(["POST"])
def generate_structured_questions(request):
    """生成结构化题目 - 使用统一的出题服务"""
    try:
        # 解析请求数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': '请求数据格式错误',
                'error_code': 'JSON_DECODE_ERROR'
            }, status=400)

        selected_types = data.get('selected_types', {})
        preferences = data.get('preferences', '')
        requirement_text = data.get('requirement_text', '')

        # 验证必要参数
        if not selected_types:
            return JsonResponse({
                'success': False,
                'error': '请选择至少一种题目类型',
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # 验证题目数量
        total_questions = sum(type_info.get('count', 0) for type_info in selected_types.values())
        if total_questions <= 0:
            return JsonResponse({
                'success': False,
                'error': '请设置有效的题目数量',
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        if total_questions > 20:
            return JsonResponse({
                'success': False,
                'error': '题目总数不能超过20道',
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # 获取用户ID
        user_id = get_user_id_from_request(request)
        logger.info(f"当前用户ID: {user_id}")

        # 检查是否是调试模式
        if data.get('debug_mode'):
            return JsonResponse({
                'debug_info': {
                    'user_id': user_id,
                    'request_user': str(request.user) if hasattr(request, 'user') else 'No user',
                    'session_key': request.session.session_key,
                    'available_notes': []
                }
            })

        # 获取最新笔记内容
        notes_content = get_user_latest_notes(user_id)
        logger.info(f"笔记内容长度: {len(notes_content)}")

        # 检查是否有有效的笔记内容
        if not notes_content or notes_content.startswith("暂无笔记内容"):
            # 添加详细的调试信息
            debug_info = {
                'user_id': user_id,
                'notes_content_preview': notes_content[:100] if notes_content else 'None',
                'request_user': str(request.user) if hasattr(request, 'user') else 'No user'
            }
            logger.error(f"NO_NOTES错误 - 调试信息: {debug_info}")

            return JsonResponse({
                'success': False,
                'error': '暂无笔记内容，请先上传文档并生成笔记',
                'error_code': 'NO_NOTES',
                'debug_info': debug_info
            }, status=400)

        # 使用统一的出题服务生成题目
        logger.info(f"开始生成题目，类型: {selected_types}")

        result = question_service.generate_questions(
            notes_content=notes_content,
            question_types=selected_types,
            user_preferences=preferences,
            user_id=user_id
        )

        # 增强响应信息
        if result.get('success'):
            questions = result.get('questions', [])
            logger.info(f"成功生成 {len(questions)} 道题目")

            # 添加题目统计信息
            type_counts = {}
            for question in questions:
                q_type = question.get('type', '未知')
                type_counts[q_type] = type_counts.get(q_type, 0) + 1

            result['type_counts'] = type_counts
            result['total_count'] = len(questions)

            # 生成友好的总结信息
            if not result.get('questions_summary'):
                summary_parts = []
                for q_type, count in type_counts.items():
                    summary_parts.append(f"{count}道{q_type}")
                result['questions_summary'] = f"成功生成了{', '.join(summary_parts)}，共{len(questions)}道题目！"

            # 保存题目到文件（如果生成成功）
            try:
                save_questions_to_file(questions, user_id)
                logger.info("题目已保存到文件")
            except Exception as e:
                # 保存失败不影响题目生成结果，只记录日志
                logger.warning(f"保存题目到文件失败: {e}")
        else:
            logger.error(f"题目生成失败: {result.get('error', '未知错误')}")

        return JsonResponse(result)

    except Exception as e:
        return error_handler.create_error_response(
            error_handler.handle_system_error(e, "题目生成")
        )

def get_latest_notes_content(user_id=None):
    """获取最新笔记内容"""
    try:
        # 如果没有提供用户ID，使用默认用户ID 1
        if user_id is None:
            user_id = '1'

        # 修正路径，指向正确的笔记目录
        media_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', str(user_id), 'output')
        print(f"查找笔记目录: {media_dir}")

        if not os.path.exists(media_dir):
            print(f"笔记目录不存在: {media_dir}")
            return "暂无笔记内容，请先生成笔记"

        # 获取最新的笔记文件夹
        folders = []
        for f in os.listdir(media_dir):
            folder_path = os.path.join(media_dir, f)
            if os.path.isdir(folder_path):
                notes_file = os.path.join(folder_path, 'notes.md')
                if os.path.exists(notes_file):
                    folders.append({
                        'name': f,
                        'path': folder_path,
                        'created': os.path.getctime(folder_path)
                    })

        if not folders:
            print("未找到任何笔记文件")
            return "暂无笔记内容，请先生成笔记"

        # 按创建时间排序，获取最新的
        latest_folder = max(folders, key=lambda x: x['created'])
        print(f"找到最新笔记文件夹: {latest_folder['name']}")

        # 读取笔记内容
        notes_file = os.path.join(latest_folder['path'], 'notes.md')
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"成功读取笔记内容，长度: {len(content)} 字符")
                # 限制内容长度，避免token过多，但保留更多内容用于生成题目
                return content[:8000] if len(content) > 8000 else content

        return "暂无笔记内容，请先生成笔记"

    except Exception as e:
        print(f"获取笔记内容失败: {e}")
        return "暂无笔记内容，请先生成笔记"


@csrf_exempt
@require_http_methods(["POST"])
def submit_answer(request):
    """提交答案API"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_index = data.get('question_index')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer')
        question_text = data.get('question_text')
        question_type = data.get('question_type')
        time_spent = data.get('time_spent', 0)

        # 验证必要参数
        if not all([session_id, question_index is not None, user_answer, correct_answer]):
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            }, status=400)

        # 获取用户ID
        user_id = get_user_id_from_request(request)

        # 判断答案是否正确
        is_correct = check_answer_correctness(user_answer, correct_answer, question_type)

        # 创建答题记录
        answer_record = {
            'session_id': session_id,
            'question_index': question_index,
            'question_type': question_type,
            'question_text': question_text,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'time_spent': time_spent,
            'answered_at': datetime.now().isoformat()
        }

        # 保存到文件
        save_answer_record(answer_record, user_id, session_id)

        # 生成解析
        explanation = generate_answer_explanation(
            question_text, question_type, user_answer, correct_answer, is_correct
        )

        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'explanation': explanation,
            'message': '答案已提交'
        })

    except Exception as e:
        logger.error(f"提交答案失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'提交答案失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_answer_report(request):
    """生成答题报告API"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')

        if not session_id:
            return JsonResponse({
                'success': False,
                'error': '缺少会话ID'
            }, status=400)

        # 获取用户ID
        user_id = get_user_id_from_request(request)

        # 读取答题记录
        answer_records = load_answer_records(user_id, session_id)

        if not answer_records:
            # 添加调试信息
            from django.conf import settings
            import glob

            debug_info = {
                'user_id': user_id,
                'session_id': session_id,
                'search_pattern': os.path.join(settings.MEDIA_ROOT, str(user_id), 'output', 'questions', '*', 'answers.json'),
                'found_files': []
            }

            # 查找所有答题记录文件
            pattern = os.path.join(settings.MEDIA_ROOT, str(user_id), 'output', 'questions', '*', 'answers.json')
            files = glob.glob(pattern)
            debug_info['found_files'] = files

            # 查找所有session_id
            all_sessions = []
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        records = json.load(f)
                    for record in records:
                        if record.get('session_id'):
                            all_sessions.append(record.get('session_id'))
                except:
                    continue

            debug_info['all_session_ids'] = list(set(all_sessions))

            logger.warning(f"未找到答题记录 - 调试信息: {debug_info}")

            return JsonResponse({
                'success': False,
                'error': '未找到答题记录，请先完成答题后再查看报告',
                'debug_info': debug_info if settings.DEBUG else None
            }, status=404)

        # 生成答题报告
        report = create_answer_report(answer_records, user_id)

        return JsonResponse({
            'success': True,
            'report': report
        })

    except Exception as e:
        logger.error(f"生成答题报告失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'生成答题报告失败: {str(e)}'
        }, status=500)


def check_answer_correctness(user_answer, correct_answer, question_type):
    """检查答案是否正确"""
    try:
        user_answer = str(user_answer).strip()
        correct_answer = str(correct_answer).strip()

        if question_type in ['选择题', '判断题']:
            # 选择题和判断题精确匹配
            return user_answer.upper() == correct_answer.upper()
        elif question_type == '填空题':
            # 填空题去除空格后比较
            return user_answer.replace(' ', '').lower() == correct_answer.replace(' ', '').lower()
        else:
            # 解答题等其他题型，简单的包含关系判断
            return correct_answer.lower() in user_answer.lower() or user_answer.lower() in correct_answer.lower()
    except:
        return False


def save_answer_record(answer_record, user_id, session_id):
    """保存答题记录到文件"""
    try:
        from django.conf import settings

        # 创建保存目录 media/[user_id]/output/questions/yyyymmdd-hhmmss/
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        save_dir = os.path.join(
            settings.MEDIA_ROOT,
            str(user_id or 'guest'),
            'output',
            'questions',
            timestamp
        )
        os.makedirs(save_dir, exist_ok=True)

        # 答题记录文件
        answers_file = os.path.join(save_dir, 'answers.json')

        # 读取现有记录
        answers = []
        if os.path.exists(answers_file):
            with open(answers_file, 'r', encoding='utf-8') as f:
                answers = json.load(f)

        # 添加新记录
        answers.append(answer_record)

        # 保存记录
        with open(answers_file, 'w', encoding='utf-8') as f:
            json.dump(answers, f, ensure_ascii=False, indent=2)

        logger.info(f"答题记录已保存到: {answers_file}")

    except Exception as e:
        logger.error(f"保存答题记录失败: {e}")


def generate_answer_explanation(question_text, question_type, user_answer, correct_answer, is_correct):
    """生成答题解析"""
    try:
        if is_correct:
            base_message = "✅ 回答正确！"
        else:
            base_message = f"❌ 回答错误。正确答案是：{correct_answer}"

        # 尝试使用AI生成详细解析
        try:
            prompt = f"""请为以下题目提供简洁的解析说明：

题目类型：{question_type}
题目内容：{question_text}
正确答案：{correct_answer}
用户答案：{user_answer}
答题结果：{'正确' if is_correct else '错误'}

请提供：
1. 简要的知识点说明
2. 解题思路
3. 如果答错了，说明错误原因

要求：解析简洁明了，50-100字即可。"""

            explanation = unified_client.call_api(prompt, max_tokens=300)
            if explanation and len(explanation.strip()) > 10:
                return f"{base_message}\n\n{explanation.strip()}"
        except Exception as e:
            logger.warning(f"AI解析生成失败: {e}")

        # 备用解析
        if question_type == '选择题':
            return f"{base_message}\n\n这是一道选择题，需要根据题目内容选择最合适的答案。"
        elif question_type == '填空题':
            return f"{base_message}\n\n这是一道填空题，需要准确填写关键词或概念。"
        elif question_type == '判断题':
            return f"{base_message}\n\n这是一道判断题，需要根据题目描述判断正误。"
        else:
            return f"{base_message}\n\n请参考学习笔记中的相关内容进行理解。"

    except Exception as e:
        logger.error(f"生成解析失败: {e}")
        return "解析生成失败，请参考学习笔记。"


def load_answer_records(user_id, session_id):
    """加载答题记录"""
    try:
        from django.conf import settings
        import glob

        # 查找答题记录文件
        pattern = os.path.join(
            settings.MEDIA_ROOT,
            str(user_id or 'guest'),
            'output',
            'questions',
            '*',
            'answers.json'
        )

        files = glob.glob(pattern)

        for file_path in sorted(files, reverse=True):  # 最新的文件优先
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)

                # 筛选指定会话的记录
                session_records = [r for r in records if r.get('session_id') == session_id]
                if session_records:
                    return session_records
            except Exception as e:
                logger.warning(f"读取答题记录文件失败: {file_path}, {e}")
                continue

        return []

    except Exception as e:
        logger.error(f"加载答题记录失败: {e}")
        return []


def create_answer_report(answer_records, user_id):
    """创建答题报告"""
    try:
        # 统计答题情况
        total_questions = len(answer_records)
        correct_count = sum(1 for r in answer_records if r.get('is_correct'))
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0

        # 按题型统计
        type_stats = {}
        weak_points = []

        for record in answer_records:
            q_type = record.get('question_type', '未知')
            if q_type not in type_stats:
                type_stats[q_type] = {'total': 0, 'correct': 0}

            type_stats[q_type]['total'] += 1
            if record.get('is_correct'):
                type_stats[q_type]['correct'] += 1
            else:
                # 收集错题信息
                weak_points.append({
                    'question': record.get('question_text', ''),
                    'type': q_type,
                    'user_answer': record.get('user_answer', ''),
                    'correct_answer': record.get('correct_answer', '')
                })

        # 生成AI报告
        try:
            report_prompt = f"""请根据以下答题数据生成一份简洁的学习报告：

总题数：{total_questions}
正确题数：{correct_count}
正确率：{accuracy:.1f}%

各题型表现：
"""
            for q_type, stats in type_stats.items():
                type_accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                report_prompt += f"- {q_type}：{stats['correct']}/{stats['total']} ({type_accuracy:.1f}%)\n"

            if weak_points:
                report_prompt += f"\n错题数量：{len(weak_points)}道\n"

            report_prompt += """
请生成一份包含以下内容的学习报告：
1. 总体表现评价
2. 各题型掌握情况分析
3. 薄弱知识点总结
4. 学习建议

要求：语言简洁友好，适合学生阅读，200-300字。"""

            ai_report = unified_client.call_api(report_prompt, max_tokens=500)

        except Exception as e:
            logger.warning(f"AI报告生成失败: {e}")
            ai_report = f"您本次答题表现良好！总共完成{total_questions}道题目，正确率为{accuracy:.1f}%。建议继续加强练习，巩固知识点。"

        # 构建完整报告
        report = {
            'summary': {
                'total_questions': total_questions,
                'correct_count': correct_count,
                'accuracy': round(accuracy, 1),
                'type_stats': type_stats
            },
            'ai_analysis': ai_report,
            'weak_points': weak_points[:5],  # 只显示前5个错题
            'recommendations': [
                "回顾错题，理解错误原因",
                "重点复习薄弱知识点",
                "多做相关练习题巩固",
                "定期复习已学内容"
            ]
        }

        # 保存报告
        save_answer_report(report, user_id)

        return report

    except Exception as e:
        logger.error(f"创建答题报告失败: {e}")
        return {
            'summary': {'total_questions': 0, 'correct_count': 0, 'accuracy': 0},
            'ai_analysis': '报告生成失败，请稍后重试。',
            'weak_points': [],
            'recommendations': []
        }


def save_answer_report(report, user_id):
    """保存答题报告"""
    try:
        from django.conf import settings

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        save_dir = os.path.join(
            settings.MEDIA_ROOT,
            str(user_id or 'guest'),
            'output',
            'questions',
            timestamp
        )
        os.makedirs(save_dir, exist_ok=True)

        report_file = os.path.join(save_dir, 'report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"答题报告已保存到: {report_file}")

    except Exception as e:
        logger.error(f"保存答题报告失败: {e}")

def get_user_id_from_request(request):
    """从请求中获取用户ID"""
    if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        return request.user.id
    return 1  # 默认用户ID

# 以下函数已迁移到统一的出题服务中，保留用于向后兼容

def build_question_prompt(selected_types, preferences, notes_content):
    """构建AI提示词（已弃用，重定向到统一服务）"""
    print("build_question_prompt已弃用，请使用统一的出题服务")
    return ""

def generate_questions_with_ai(selected_types, notes_content, user_id):
    """使用AI生成题目（已弃用，重定向到统一服务）"""
    print("generate_questions_with_ai已弃用，重定向到统一服务")
    result = question_service.generate_questions(
        notes_content=notes_content,
        question_types=selected_types,
        user_preferences="",
        user_id=user_id
    )
    return result.get('questions', [])

# 文件结束
