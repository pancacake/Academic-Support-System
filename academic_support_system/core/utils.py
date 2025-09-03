"""
核心工具函数
"""
import os
from django.conf import settings

def get_user_latest_notes(user_id):
    """获取用户最新的笔记内容"""
    try:
        # 首先尝试从用户的output目录中获取最新笔记
        user_output_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), 'output')

        if os.path.exists(user_output_dir):
            # 获取所有时间戳目录，找到最新的
            timestamp_dirs = [d for d in os.listdir(user_output_dir)
                            if os.path.isdir(os.path.join(user_output_dir, d)) and
                            d.replace('-', '').replace('_', '').isdigit()]

            if timestamp_dirs:
                # 按时间戳排序，获取最新的
                latest_dir = max(timestamp_dirs)
                contents_file = os.path.join(user_output_dir, latest_dir, 'contents.md')

                if os.path.exists(contents_file):
                    with open(contents_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            print(f"✅ 从 {contents_file} 读取笔记成功，长度: {len(content)}")
                            return content

                # 如果contents.md不存在，尝试notes.md
                notes_file = os.path.join(user_output_dir, latest_dir, 'notes.md')
                if os.path.exists(notes_file):
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            print(f"✅ 从 {notes_file} 读取笔记成功，长度: {len(content)}")
                            return content

        # 备用方案：从数据库获取
        try:
            from notes.models import Note
            latest_note = Note.objects.filter(user_id=user_id).order_by('-created_at').first()

            if latest_note and latest_note.content:
                print(f"✅ 从数据库读取笔记成功，长度: {len(latest_note.content)}")
                return latest_note.content
        except Exception as db_error:
            print(f"数据库查询失败: {db_error}")

        # 最后备用方案：从notes目录读取
        notes_dir = os.path.join(settings.MEDIA_ROOT, 'notes', str(user_id))
        if os.path.exists(notes_dir):
            note_files = [f for f in os.listdir(notes_dir) if f.endswith(('.txt', '.md'))]
            if note_files:
                latest_file = max(note_files, key=lambda x: os.path.getctime(os.path.join(notes_dir, x)))
                with open(os.path.join(notes_dir, latest_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        print(f"✅ 从备用目录读取笔记成功，长度: {len(content)}")
                        return content

        print(f"❌ 用户 {user_id} 没有找到任何笔记内容")
        return "暂无笔记内容，请先上传文档并生成笔记"

    except Exception as e:
        print(f"获取笔记失败: {e}")
        import traceback
        traceback.print_exc()
        return "暂无笔记内容，请先上传文档并生成笔记"

def get_user_id_from_request(request):
    """从请求中获取用户ID"""
    if request.user.is_authenticated:
        return str(request.user.id)

    # 游客模式
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    return f"guest_{session_id}"

def save_generated_questions(user_id, questions_data):
    """保存生成的题目到用户的notes目录"""
    try:
        import json
        from datetime import datetime

        # 创建用户的notes目录
        user_notes_dir = os.path.join(settings.MEDIA_ROOT, str(user_id), 'output', 'notes')
        os.makedirs(user_notes_dir, exist_ok=True)

        # 生成文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        questions_file = os.path.join(user_notes_dir, f'questions_{timestamp}.json')

        # 保存题目数据
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 题目已保存到: {questions_file}")
        return questions_file

    except Exception as e:
        print(f"保存题目失败: {e}")
        return None

def get_user_notes_directory(user_id):
    """获取用户的notes目录路径"""
    return os.path.join(settings.MEDIA_ROOT, str(user_id), 'output', 'notes')
