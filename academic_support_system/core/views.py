import os
import json
import threading
import time
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# 删除了认证相关的导入
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.conf import settings
import importlib.util
from django.shortcuts import render
from .question_generator import generate_questions_from_notes, check_answer_correctness

# 动态导入 file_parsers
file_parsers_path = os.path.join(settings.BASE_DIR, 'file_parsers.py')
spec = importlib.util.spec_from_file_location('file_parsers', file_parsers_path)
file_parsers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_parsers)

def login_portal(request):
    """登录门户页面"""
    return render(request, 'login_portal.html')

def check_auth_and_redirect(request):
    """检查认证状态并重定向"""
    # 检查是否已登录
    if request.user.is_authenticated:
        return redirect('/')

    # 检查是否是游客模式
    if request.session.get('guest_mode'):
        return redirect('/')

    # 未登录且非游客模式，重定向到登录页面
    return redirect('/login/')

# 用户相关辅助函数
def get_user_id(request):
    """获取用户ID，未登录返回0"""
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.id
    return 0

def get_user_upload_path(user_id):
    """获取用户上传目录路径"""
    return f'media/{user_id}/uploads'

def get_user_output_path(user_id):
    """获取用户输出目录路径"""
    return f'media/{user_id}/output'

# 全局变量存储生成状态
generation_status = {}

# 进度回调函数
def progress_callback(current=None, total=None, message=""):
    """进度回调函数，用于更新解析进度"""
    try:
        if current is not None and total is not None and total > 0:
            progress_percent = int((current / total) * 100)
            default_message = f"正在解析第 {current}/{total} 张图片..."
        else:
            progress_percent = 0
            default_message = "正在处理..."

        generation_status['current'] = {
            'status': 'processing',
            'progress': progress_percent,
            'current': current,
            'total': total,
            'message': message or default_message
        }
    except Exception as e:
        print(f"Progress callback error: {e}")
        # 即使进度回调出错，也不影响主流程

# 删除重复的get_user_id函数，使用上面定义的版本

# 删除了所有认证相关的视图函数

def simple_chat_view(request):
    """主聊天页面 - 需要认证或游客模式"""
    # 检查认证状态
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('/login/')

    from django.shortcuts import render
    return render(request, 'simple_chat.html')

def questions_view(request):
    """出题页面 - 需要认证或游客模式"""
    # 检查认证状态
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('/login/')

    from django.shortcuts import render
    return render(request, 'questions.html')

@api_view(['GET'])
def get_csrf_token(request):
    from django.middleware.csrf import get_token
    token = get_token(request)
    return Response({'csrf_token': token})

@api_view(['GET'])
def get_user_latest_notes(request):
    """获取用户最新的笔记内容"""
    try:
        user_id = get_user_id(request)
        output_dir = get_user_output_path(user_id)

        if not os.path.exists(output_dir):
            return Response({'success': False, 'error': '没有找到笔记文件'}, status=404)

        # 获取最新的时间戳目录
        timestamp_dirs = [d for d in os.listdir(output_dir)
                         if os.path.isdir(os.path.join(output_dir, d))]

        if not timestamp_dirs:
            return Response({'success': False, 'error': '没有找到笔记文件'}, status=404)

        # 按时间戳排序，获取最新的
        latest_dir = sorted(timestamp_dirs)[-1]
        latest_path = os.path.join(output_dir, latest_dir)

        # 查找笔记文件
        notes_file = None
        contents_file = None

        for file in os.listdir(latest_path):
            if file == 'notes.md':
                notes_file = os.path.join(latest_path, file)
            elif file == 'contents.md':
                contents_file = os.path.join(latest_path, file)

        if not notes_file:
            return Response({'success': False, 'error': '没有找到笔记文件'}, status=404)

        # 读取笔记内容
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes_content = f.read()

        # 读取目录内容（如果存在）
        toc_content = None
        if contents_file and os.path.exists(contents_file):
            with open(contents_file, 'r', encoding='utf-8') as f:
                toc_content = f.read()

        return Response({
            'success': True,
            'notes_content': notes_content,
            'toc_content': toc_content,
            'timestamp': latest_dir
        })

    except Exception as e:
        return Response({'success': False, 'error': f'获取笔记失败：{str(e)}'}, status=500)

# 删除了登录页面视图

@csrf_exempt
@api_view(['POST'])
def upload_file(request):
    try:
        user_id = get_user_id(request)
        upload_dir = get_user_upload_path(user_id)
        os.makedirs(upload_dir, exist_ok=True)
        # 限制最多5个文件
        existing_files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
        if len(existing_files) >= 5:
            generation_status['current'] = {
                'status': 'limit_reached',
                'message': '文件数量已达上限。每位用户最多只能上传5个文件。如需上传新文件，请先删除旧文件。'
            }
            return Response({'success': False, 'error': '文件数量已达上限。每位用户最多只能上传5个文件。如需上传新文件，请先删除旧文件。'}, status=400)
        if request.method == 'POST' and request.FILES.get('file'):
            upload = request.FILES['file']
            file_name = upload.name
            file_path = os.path.join(upload_dir, file_name)

            # 检查文件格式
            supported_formats = file_parsers.get_supported_formats()
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext not in supported_formats:
                generation_status['current'] = {
                    'status': 'error',
                    'message': f'不支持的文件格式：{file_ext}。支持的格式：{", ".join(supported_formats)}'
                }
                return Response({'success': False, 'error': f'不支持的文件格式：{file_ext}'}, status=400)

        try:
            # 设置上传状态
            generation_status['current'] = {
                'status': 'uploading',
                'message': f'正在上传文件：{file_name}...',
                'progress': 0
            }

            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in upload.chunks():
                    destination.write(chunk)

            # 上传成功状态
            generation_status['current'] = {
                'status': 'upload_success',
                'message': f'文件"{file_name}"上传成功，正在准备解析...',
                'progress': 100
            }
            # 解析文件并输出到聊天框
            def process_file():
                try:
                    # 解析目录结构 - 使用文件名（不含扩展名）作为目录名
                    file_name_without_ext = os.path.splitext(file_name)[0]
                    parsed_dir = os.path.join(upload_dir, file_name_without_ext)
                    os.makedirs(parsed_dir, exist_ok=True)
                    images_dir = os.path.join(parsed_dir, 'images')
                    os.makedirs(images_dir, exist_ok=True)
                    # 使用统一的解析函数，传入进度回调
                    result = file_parsers.parse_file(file_path, images_dir, progress_callback)
                    json_path = os.path.join(parsed_dir, f'{os.path.splitext(file_name)[0]}.json')
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    # 反馈到聊天框
                    # 获取当前已上传的文件列表
                    uploaded_files = []
                    for item in os.listdir(upload_dir):
                        item_path = os.path.join(upload_dir, item)
                        if os.path.isdir(item_path):
                            for file in os.listdir(item_path):
                                if file.endswith('.json'):
                                    uploaded_files.append(os.path.splitext(file)[0])

                    files_list = "、".join(uploaded_files) if uploaded_files else "无"
                    msg = f'文件“{file_name}”已成功解析！\n\n📁 当前已上传的文件：{files_list}\n\n💡 是否开始生成学习笔记？请回复"是"或"开始生成笔记"来开始。'
                    generation_status['current'] = {
                        'status': 'completed',
                        'message': msg,
                        'result': result,
                        'progress': 100,
                        'ask_for_notes': True,
                        'uploaded_files': uploaded_files
                    }
                except Exception as e:
                    generation_status['current'] = {
                        'status': 'error',
                        'message': f'文件“{file_name}”解析失败：{str(e)}'
                    }
            thread = threading.Thread(target=process_file)
            thread.daemon = True
            thread.start()
            return Response({'success': True, 'message': f'文件“{file_name}”上传成功，正在为您解析，请稍候...'}, status=200)
        except Exception as e:
            return Response({'success': False, 'error': f'文件上传失败：{str(e)}'}, status=400)

        return Response({'success': False, 'error': '未检测到上传文件。'}, status=400)

    except Exception as e:
        return Response({'success': False, 'error': f'上传处理失败：{str(e)}'}, status=500)

@api_view(['GET'])
def get_generation_status(request):
    # 首先检查笔记生成状态
    try:
        from notes.views import note_generation_status
        if 'current' in note_generation_status:
            note_status = note_generation_status['current']
            # 如果笔记正在生成或已完成，优先返回笔记状态
            if note_status.get('status') in ['generating', 'completed', 'error']:
                return Response(note_status)
    except ImportError:
        pass

    # 如果没有笔记生成状态，返回文件处理状态
    if 'current' not in generation_status:
        return Response({'status': 'none', 'message': '暂无解析任务。'})
    return Response(generation_status['current'])

@api_view(['GET'])
def get_notes_content(request):
    file_name = request.GET.get('file_name')
    if not file_name:
        return Response({'error': '参数缺失。'}, status=400)
    file_name_without_ext = os.path.splitext(file_name)[0]
    parsed_dir = os.path.join('media', 'uploads', file_name_without_ext)
    json_path = os.path.join(parsed_dir, f'{file_name_without_ext}.json')
    if not os.path.exists(json_path):
        return Response({'error': '笔记文件不存在。'}, status=404)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response({'content': content})
    except Exception as e:
        return Response({'error': f'读取笔记失败：{str(e)}'}, status=500)

@api_view(['GET'])
def stream_notes_content(request):
    user_id = str(request.user.id) if (request and hasattr(request, 'user') and request.user and request.user.is_authenticated) else None
    file_name = request.GET.get('file_name')
    if not user_id or not file_name:
        return Response({'error': '参数缺失。'}, status=400)
    parsed_dir = os.path.join('media', user_id, 'uploads', file_name)
    json_path = os.path.join(parsed_dir, f'{os.path.splitext(file_name)[0]}.json')
    if not os.path.exists(json_path):
        return Response({'error': '笔记文件不存在。'}, status=404)
    def generate():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            yield f'Error: {str(e)}'
    response = StreamingHttpResponse(generate(), content_type='text/plain; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    return response

@api_view(['POST'])
def chat_message(request):
    try:
        print(f"[DEBUG] 收到聊天请求: {request.method}")
        print(f"[DEBUG] 请求头: {dict(request.headers)}")
        print(f"[DEBUG] 请求类型: {type(request)}")
        print(f"[DEBUG] 用户对象: {getattr(request, 'user', 'No user attribute')}")
        data = request.data
        message = data.get('message', '')
        print(f"[DEBUG] 消息内容: {message}")
        # 检查是否要生成笔记
        note_keywords = ['是', '开始生成笔记', '生成笔记', '开始生成', '生成', '笔记', 'yes', 'start']
        if any(keyword in message.lower() for keyword in note_keywords):
            # 首先检查用户是否有已解析的文件
            from notes.views import get_user_id, get_user_upload_path
            import os

            user_id = get_user_id(request)
            upload_dir = get_user_upload_path(user_id)
            print(f"[DEBUG] 用户认证状态: {request.user.is_authenticated if hasattr(request, 'user') else 'No user'}")
            print(f"[DEBUG] 用户对象: {request.user if hasattr(request, 'user') else 'No user'}")
            print(f"[DEBUG] 检查用户 {user_id} 的上传目录: {upload_dir}")
            print(f"[DEBUG] 目录是否存在: {os.path.exists(upload_dir)}")

            if not os.path.exists(upload_dir):
                # 检查是否是因为用户未登录导致的user_id=0
                if user_id == 0:
                    return Response({
                        'success': True,
                        'response': '请先登录后再使用笔记生成功能。您可以点击右上角的登录按钮进行登录。'
                    })
                else:
                    return Response({
                        'success': True,
                        'response': '抱歉，您还没有上传任何文档。请先上传PDF、Word或PPT文档，系统解析后才能生成笔记。'
                    })

            # 查找已解析的JSON文件
            json_files = []
            for item in os.listdir(upload_dir):
                item_path = os.path.join(upload_dir, item)
                if os.path.isdir(item_path):
                    for file in os.listdir(item_path):
                        if file.endswith('.json'):
                            json_files.append(file)

            if not json_files:
                return Response({
                    'success': True,
                    'response': '抱歉，没有找到已解析的文档。请确保您上传的文档已经成功解析完成。'
                })

            print(f"[DEBUG] 找到 {len(json_files)} 个已解析的文件: {json_files}")
            # 直接调用笔记生成函数
            try:
                from notes.views import start_note_generation
                from django.http import HttpRequest
                import json

                # 创建Django原生HttpRequest对象
                django_request = HttpRequest()
                django_request.method = 'POST'
                django_request.user = request.user
                django_request.session = getattr(request, 'session', {})
                django_request.META = getattr(request, 'META', {})
                django_request._body = b'{}'

                print(f"[DEBUG] 调用笔记生成，用户: {django_request.user}")
                print(f"[DEBUG] 用户ID: {django_request.user.id if hasattr(django_request.user, 'id') else 'No ID'}")
                print(f"[DEBUG] 用户认证状态: {django_request.user.is_authenticated if hasattr(django_request.user, 'is_authenticated') else 'No auth'}")
                print(f"[DEBUG] 请求类型: {type(django_request)}")
                result = start_note_generation(django_request)
                print(f"[DEBUG] 笔记生成调用完成，结果类型: {type(result)}")

                # 处理不同类型的Response对象
                if hasattr(result, 'data'):
                    # DRF Response对象可以直接访问data属性
                    result_data = result.data
                    if result_data.get('success'):
                        response = f"好的！{result_data.get('message', '正在开始生成笔记...')}"
                    else:
                        response = f"抱歉，{result_data.get('error', '笔记生成启动失败')}"
                elif hasattr(result, 'content'):
                    # 如果是JsonResponse，直接解析content
                    try:
                        # JsonResponse的content是bytes类型，直接解码
                        if isinstance(result.content, bytes):
                            content_str = result.content.decode('utf-8')
                        else:
                            content_str = str(result.content)

                        result_data = json.loads(content_str)
                        if result_data.get('success'):
                            response = f"好的！{result_data.get('message', '正在开始生成笔记...')}"
                        else:
                            response = f"抱歉，{result_data.get('error', '笔记生成启动失败')}"
                    except Exception as e:
                        print(f"[ERROR] 解析响应内容失败: {e}")
                        print(f"[ERROR] 响应类型: {type(result)}")
                        print(f"[ERROR] 响应内容: {getattr(result, 'content', 'No content')}")
                        response = "笔记生成已启动，请稍候..."
                else:
                    response = "笔记生成已启动，请稍候..."

            except Exception as e:
                print(f"[ERROR] 笔记生成启动失败: {e}")
                if "没有找到已解析的文件" in str(e):
                    response = "抱歉，启动笔记生成时出现错误：没有找到已解析的文件。请先上传并解析文档后再生成笔记。"
                else:
                    response = f"抱歉，启动笔记生成时出现错误：{str(e)}"
        # 普通对话 - 检查是否包含@符号
        else:
            # 检查是否是修改确认
            if message.strip() in ['确认修改', '确认', '是的', '是']:
                try:
                    response = handle_modification_confirmation(request)
                except Exception as e:
                    print(f"[ERROR] 处理修改确认失败: {e}")
                    response = f"处理修改确认时出现错误：{str(e)}"
            # 检查是否包含@符号，进入AI问答环节
            elif '@' in message:
                try:
                    response = handle_section_qa_or_modification(message, request)
                except Exception as e:
                    print(f"[ERROR] 处理@消息失败: {e}")
                    response = f"处理您的问题时出现错误：{str(e)}"
            else:
                # 普通AI聊天功能
                try:
                    from notes.views import ai_chat_with_notes
                    from django.http import HttpRequest
                    import json

                    # 创建模拟请求
                    mock_request = HttpRequest()
                    mock_request.method = 'POST'
                    mock_request._body = json.dumps({'message': message}).encode('utf-8')
                    mock_request.content_type = 'application/json'
                    mock_request.user = request.user if hasattr(request, 'user') else None

                    # 模拟request.data
                    class MockData:
                        def get(self, key, default=None):
                            data = json.loads(mock_request._body.decode('utf-8'))
                            return data.get(key, default)

                    mock_request.data = MockData()

                    # 调用AI聊天
                    result = ai_chat_with_notes(mock_request)

                    if hasattr(result, 'data'):
                        result_data = result.data
                        if result_data.get('success'):
                            response = result_data.get('message', '')

                            # 如果是章节更新，添加提示
                            if not result_data.get('is_general_chat'):
                                response += f"\n\n✅ 已更新笔记中的「{result_data.get('section_title', '')}」部分"
                        else:
                            # AI聊天失败，使用简单回复
                            if '你好' in message or 'hello' in message.lower():
                                response = "您好，欢迎使用 academic support system！我是您的智能服务助手，可以为您解析文档、整理笔记、解答问题。"
                            elif '帮助' in message or 'help' in message.lower():
                                response = "您可以上传PDF、PPT、Word文档，我会自动为您解析并整理内容。每位用户最多可上传5个文件。还有其它问题也欢迎随时咨询！"
                            else:
                                response = "您的消息已收到。如需解析文档，请先上传文件。如需修改笔记内容，请说'修改XXX部分'。"
                    else:
                        response = "您的消息已收到。如需解析文档，请先上传文件。"

                except Exception as e:
                    print(f"[ERROR] AI聊天失败: {e}")
                    # AI聊天出错，使用简单回复
                    if '你好' in message or 'hello' in message.lower():
                        response = "您好，欢迎使用 academic support system！我是您的智能服务助手，可以为您解析文档、整理笔记、解答问题。"
                    elif '帮助' in message or 'help' in message.lower():
                        response = "您可以上传PDF、PPT、Word文档，我会自动为您解析并整理内容。每位用户最多可上传5个文件。还有其它问题也欢迎随时咨询！"
                    else:
                        response = f"收到您的消息：{message}。如需修改笔记内容，请说'修改XXX部分'。"
        return Response({'success': True, 'response': response})

    except Exception as e:
        print(f"[ERROR] 聊天处理失败: {e}")
        return Response({'success': False, 'error': f'处理失败：{str(e)}'}, status=500)

def handle_section_qa_or_modification(message, request):
    """处理@章节的问答或修改请求"""
    import re
    from notes.views import get_user_id, get_latest_notes_file, extract_section_content
    from notes.note_generator import get_api_client
    from prompts import SECTION_QA_PROMPT, SECTION_MODIFICATION_PROMPT

    # 解析@章节名称
    at_pattern = r'@([^@\s]+)'
    matches = re.findall(at_pattern, message)

    if not matches:
        return "请使用@符号指定要询问的章节，例如：@网络基础概念 这个概念是什么意思？"

    section_title = matches[0]

    # 移除@章节名称，获取用户的实际问题
    user_question = re.sub(r'@[^@\s]+\s*', '', message).strip()

    if not user_question:
        return f"请在@{section_title}后面提出您的问题。"

    # 获取笔记内容
    user_id = get_user_id(request)
    latest_notes = get_latest_notes_file(user_id)

    if not latest_notes:
        return "没有找到笔记文件，请先生成笔记。"

    # 读取笔记内容
    try:
        with open(latest_notes['notes_file'], 'r', encoding='utf-8') as f:
            notes_content = f.read()
    except Exception as e:
        return f"读取笔记文件失败：{str(e)}"

    # 提取指定章节的内容
    section_content = extract_section_content(notes_content, section_title)

    if not section_content:
        return f"没有找到章节「{section_title}」，请检查章节名称是否正确。"

    # 检查是否是修改请求
    modification_keywords = ['修改', '更新', '改进', '完善', '调整', '重写', '优化', '补充']
    is_modification = any(keyword in user_question for keyword in modification_keywords)

    if is_modification:
        # 修改逻辑：先确认用户意图，将信息存储到session
        if not hasattr(request, 'session'):
            request.session = {}

        request.session['pending_modification'] = {
            'section_title': section_title,
            'section_content': section_content,
            'modification_request': user_question,
            'notes_file': latest_notes['notes_file']
        }

        return f"您希望修改章节「{section_title}」吗？\n\n您的修改要求：{user_question}\n\n请回复\"确认修改\"来继续，或者重新描述您的需求。"
    else:
        # 问答逻辑：使用系统提示词A
        return generate_section_qa_response(section_title, section_content, user_question)

def generate_section_qa_response(section_title, section_content, user_question):
    """生成章节问答回复"""
    try:
        from notes.note_generator import get_api_client
        from prompts import SECTION_QA_PROMPT

        client = get_api_client()
        if not client:
            return "抱歉，AI服务暂时不可用。"

        # 使用系统提示词A
        prompt = SECTION_QA_PROMPT.format(
            section_title=section_title,
            section_content=section_content,
            user_question=user_question
        )

        response = client.chat_completion([
            {"role": "user", "content": prompt}
        ])

        return f"📖 关于章节「{section_title}」的解答：\n\n{response.strip()}"

    except Exception as e:
        return f"生成回复时出错：{str(e)}"

def generate_section_modification(section_title, section_content, modification_request):
    """生成章节修改内容"""
    try:
        from notes.note_generator import get_api_client
        from prompts import SECTION_MODIFICATION_PROMPT

        client = get_api_client()
        if not client:
            return None, "抱歉，AI服务暂时不可用。"

        # 使用系统提示词B
        prompt = SECTION_MODIFICATION_PROMPT.format(
            section_title=section_title,
            section_content=section_content,
            modification_request=modification_request
        )

        response = client.chat_completion([
            {"role": "user", "content": prompt}
        ])

        return response.strip(), None

    except Exception as e:
        return None, f"生成修改内容时出错：{str(e)}"

def handle_modification_confirmation(request):
    """处理修改确认"""
    if not hasattr(request, 'session') or 'pending_modification' not in request.session:
        return "没有待确认的修改请求。"

    pending = request.session['pending_modification']
    section_title = pending['section_title']
    section_content = pending['section_content']
    modification_request = pending['modification_request']
    notes_file = pending['notes_file']

    # 生成修改后的内容
    modified_content, error = generate_section_modification(
        section_title, section_content, modification_request
    )

    if error:
        return f"修改失败：{error}"

    # 更新笔记文件
    try:
        # 读取完整的笔记内容
        with open(notes_file, 'r', encoding='utf-8') as f:
            full_notes_content = f.read()

        # 替换章节内容
        updated_notes = replace_section_content(full_notes_content, section_title, modified_content)

        # 写回文件
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(updated_notes)

        # 清除session中的待修改信息
        del request.session['pending_modification']

        return f"✅ 已成功修改章节「{section_title}」！\n\n修改后的内容已保存到笔记文件中。您可以在右侧笔记面板查看更新后的内容。"

    except Exception as e:
        return f"保存修改时出错：{str(e)}"

def replace_section_content(full_content, section_title, new_content):
    """替换笔记中指定章节的内容"""
    lines = full_content.split('\n')
    result_lines = []
    in_target_section = False
    current_level = 0

    for line in lines:
        # 检查是否是标题行
        if line.strip().startswith('#'):
            # 计算标题级别
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break

            # 提取标题文本
            title_text = line[level:].strip()

            # 检查是否是目标章节
            if section_title.lower() in title_text.lower() or title_text.lower() in section_title.lower():
                in_target_section = True
                current_level = level
                # 添加新的章节内容
                result_lines.append(new_content)
                continue
            elif in_target_section:
                # 如果遇到同级或更高级的标题，结束当前章节
                if level <= current_level:
                    in_target_section = False
                    result_lines.append(line)
                else:
                    # 跳过原有的子章节内容
                    continue
            else:
                result_lines.append(line)
        elif not in_target_section:
            result_lines.append(line)
        # 如果在目标章节内，跳过原有内容

    return '\n'.join(result_lines)

# 出题功能相关API
@api_view(['POST'])
@csrf_exempt
def generate_questions(request):
    """生成题目API - 使用统一的出题服务"""
    try:
        from .question_service import question_service
        from .utils import get_user_latest_notes

        data = request.data
        requirement = data.get('requirement', '')
        question_types = data.get('question_types', [])

        if not requirement:
            return Response({'success': False, 'error': '请输入出题需求'}, status=400)

        user_id = get_user_id(request)

        # 获取用户笔记内容
        notes_content = get_user_latest_notes(user_id)
        if not notes_content or notes_content.startswith("暂无笔记内容"):
            return Response({
                'success': False,
                'error': '暂无笔记内容，请先上传文档并生成笔记'
            }, status=400)

        # 解析需求为题目类型配置
        parsed_types = parse_requirement_to_types(requirement, question_types)

        # 使用统一的出题服务
        result = question_service.generate_questions(
            notes_content=notes_content,
            question_types=parsed_types,
            user_preferences=requirement,
            user_id=user_id
        )

        return Response(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'success': False, 'error': str(e)}, status=500)

def parse_requirement_to_types(requirement, question_types=None):
    """解析需求为题目类型配置"""
    # 默认配置
    default_types = {
        'multipleChoice': {'name': '选择题', 'count': 3},
        'fillBlank': {'name': '填空题', 'count': 2},
        'trueOrFalse': {'name': '判断题', 'count': 2},
        'shortAnswer': {'name': '解答题', 'count': 1}
    }

    if question_types:
        # 如果指定了题目类型，使用指定的
        parsed = {}
        for q_type in question_types:
            if q_type in default_types:
                parsed[q_type] = default_types[q_type]
        return parsed if parsed else default_types

    return default_types

@api_view(['POST'])
@csrf_exempt
def check_answer(request):
    """检查答案API"""
    try:
        data = request.data
        question_id = data.get('question_id')
        user_answer = data.get('user_answer', '')
        correct_answer = data.get('correct_answer', '')
        question_type = data.get('question_type', '选择题')

        if not user_answer:
            return Response({'success': False, 'error': '请输入答案'}, status=400)

        is_correct = check_answer_correctness(user_answer, correct_answer, question_type)

        return Response({
            'success': True,
            'is_correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'explanation': f"{'正确' if is_correct else '错误'}！正确答案是：{correct_answer}"
        })

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)