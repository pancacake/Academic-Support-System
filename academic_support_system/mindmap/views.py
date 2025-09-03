from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import os
import re
import json
import asyncio
from datetime import datetime

def get_user_id(request):
    """获取用户ID，未登录返回0"""
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user.id
    return 0

def get_user_output_path(user_id):
    """获取用户输出目录路径"""
    return os.path.join('media', str(user_id), 'output')

def mindmap_view(request, note_id=None):
    """思维导图页面 - 需要认证或游客模式"""
    # 检查认证状态
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('/login/')

    # 将note_id传递给模板（如果有的话）
    context = {}
    if note_id:
        context['note_id'] = note_id

    return render(request, 'mindmap.html', context)

@csrf_exempt
@api_view(['GET'])
def get_latest_notes(request):
    """获取最新生成的笔记文件"""
    try:
        user_id = get_user_id(request)
        output_dir = get_user_output_path(user_id)
        if not os.path.exists(output_dir):
            return Response({'success': False, 'error': '没有找到输出目录'}, status=404)

        # 获取所有输出目录，按时间排序
        folders = []
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path):
                # 检查是否有notes.md文件
                notes_file = os.path.join(item_path, 'notes.md')
                contents_file = os.path.join(item_path, 'contents.md')
                if os.path.exists(notes_file):
                    folders.append({
                        'name': item,
                        'path': item_path,
                        'notes_file': notes_file,
                        'contents_file': contents_file,
                        'created': os.path.getctime(item_path)
                    })

        if not folders:
            return Response({'success': False, 'error': '没有找到笔记文件'}, status=404)

        # 按创建时间排序，获取最新的
        latest_folder = sorted(folders, key=lambda x: x['created'], reverse=True)[0]

        # 优先读取完整的笔记文件，而不是目录文件，以获得更多内容
        content_file = latest_folder['notes_file']

        # 如果用户特别想要目录结构，可以检查contents.md
        # 但默认使用完整的notes.md以获得更丰富的内容
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 如果内容太少，尝试读取contents.md作为补充
        if len(content.strip()) < 100 and os.path.exists(latest_folder['contents_file']):
            with open(latest_folder['contents_file'], 'r', encoding='utf-8') as f:
                content = f.read()

        return Response({
            'success': True,
            'folder': latest_folder['name'],
            'content': content,
            'file_path': latest_folder['notes_file']
        })

    except Exception as e:
        return Response({'success': False, 'error': f'获取笔记失败：{str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def parse_notes_to_mindmap(request):
    """解析笔记内容为思维导图数据"""
    try:
        import json
        data = json.loads(request.body)
        content = data.get('content', '')

        if not content:
            return JsonResponse({'success': False, 'error': '笔记内容为空'}, status=400)

        # 解析Markdown标题结构
        mindmap_data = parse_markdown_headers(content)

        return JsonResponse({
            'success': True,
            'mindmap_data': mindmap_data
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'解析失败：{str(e)}'}, status=500)

def parse_markdown_headers(content):
    """解析Markdown标题为思维导图结构"""
    lines = content.split('\n')
    mindmap_data = {
        'name': '📚 学习笔记',
        'children': []
    }

    # 用于跟踪当前层级的节点
    current_nodes = {0: mindmap_data}  # 从0级开始

    # 统计找到的标题数量
    header_count = 0

    for line in lines:
        line = line.strip()
        if not line.startswith('#'):
            continue

        # 计算标题级别
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break

        if level > 6:  # Markdown最多支持6级标题
            continue

        # 提取标题文本，清理格式
        title = line[level:].strip()
        if not title:
            continue

        # 清理标题中的特殊字符和格式
        title = title.replace('**', '').replace('*', '').replace('`', '')
        title = title.strip()

        if not title:
            continue

        header_count += 1

        # 添加层级图标
        level_icons = ['📖', '📝', '📋', '📌', '🔸', '🔹']
        icon = level_icons[min(level-1, len(level_icons)-1)] if level > 0 else '📄'

        # 创建新节点
        new_node = {
            'name': f"{icon} {title}",
            'level': level,
            'children': []
        }

        # 找到父节点
        parent_level = level - 1
        while parent_level >= 0 and parent_level not in current_nodes:
            parent_level -= 1

        if parent_level >= 0:
            parent_node = current_nodes[parent_level]
            parent_node['children'].append(new_node)
        else:
            mindmap_data['children'].append(new_node)

        # 更新当前层级节点
        current_nodes[level] = new_node

        # 清除更深层级的节点
        keys_to_remove = [k for k in current_nodes.keys() if k > level]
        for k in keys_to_remove:
            del current_nodes[k]

    # 如果没有找到任何标题，创建一个默认结构
    if header_count == 0:
        mindmap_data['children'] = [
            {
                'name': '📄 内容概览',
                'children': [
                    {'name': '📝 笔记内容已加载', 'children': []},
                    {'name': '🔍 请检查原始文档格式', 'children': []},
                    {'name': '💡 建议使用Markdown标题格式', 'children': []}
                ]
            }
        ]

    return mindmap_data

@csrf_exempt
@require_http_methods(["POST"])
def update_mindmap_node(request):
    """更新思维导图节点"""
    try:
        import json
        data = json.loads(request.body)
        node_id = data.get('node_id')
        new_name = data.get('new_name')
        action = data.get('action')  # 'update', 'delete', 'add_child'

        # 这里可以实现节点的增删改逻辑
        # 为了简化，先返回成功响应

        return JsonResponse({
            'success': True,
            'message': f'节点操作成功: {action}'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'操作失败：{str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_mindmap_section(request):
    """根据笔记内容生成特定部分的思维导图"""
    try:
        import json
        data = json.loads(request.body)
        section_title = data.get('section_title')
        notes_content = data.get('notes_content')

        if not section_title or not notes_content:
            return JsonResponse({'success': False, 'error': '缺少必要参数'}, status=400)

        # 提取相关部分内容
        section_content = extract_section_content(notes_content, section_title)

        if not section_content:
            return JsonResponse({'success': False, 'error': '未找到相关内容'}, status=404)

        # 调用AI生成精炼的思维导图
        refined_mindmap = generate_refined_mindmap(section_title, section_content)

        return JsonResponse({
            'success': True,
            'refined_mindmap': refined_mindmap
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'生成失败：{str(e)}'}, status=500)

def extract_section_content(content, section_title):
    """从笔记中提取特定章节的内容"""
    lines = content.split('\n')
    section_lines = []
    in_section = False
    current_level = 0

    for line in lines:
        line_stripped = line.strip()

        # 检查是否是标题行
        if line_stripped.startswith('#'):
            level = len(line_stripped) - len(line_stripped.lstrip('#'))
            title = line_stripped[level:].strip()

            if title == section_title:
                in_section = True
                current_level = level
                section_lines.append(line)
                continue
            elif in_section and level <= current_level:
                # 遇到同级或更高级标题，结束当前章节
                break

        if in_section:
            section_lines.append(line)

    return '\n'.join(section_lines)

def generate_refined_mindmap(section_title, section_content):
    """调用AI生成精炼的思维导图"""
    # 这里需要集成现有的API客户端
    try:
        # 导入API客户端
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from api_client import APIClient

        client = APIClient()

        prompt = f"""
请根据以下内容为"{section_title}"生成一个精炼的思维导图结构。
要求：
1. 提取核心概念和关键点
2. 建立清晰的层级关系
3. 每个节点名称简洁明了
4. 最多3-4层深度

内容：
{section_content}

请以JSON格式返回思维导图结构，格式如下：
{{
    "name": "章节标题",
    "children": [
        {{
            "name": "子概念1",
            "children": [...]
        }}
    ]
}}
"""

        response = client.chat_completion([
            {"role": "user", "content": prompt}
        ])

        # 解析AI返回的JSON
        import json
        try:
            mindmap_json = json.loads(response)
            return mindmap_json
        except:
            # 如果解析失败，返回简单结构
            return {
                "name": section_title,
                "children": [
                    {"name": "AI生成失败，请手动编辑", "children": []}
                ]
            }

    except Exception as e:
        return {
            "name": section_title,
            "children": [
                {"name": f"生成失败: {str(e)}", "children": []}
            ]
        }
