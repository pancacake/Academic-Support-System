import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import importlib.util

# 导入集中管理的提示词
try:
    from prompts import NOTE_GENERATION_SYSTEM_PROMPT
except ImportError:
    # 如果导入失败，使用默认提示词
    NOTE_GENERATION_SYSTEM_PROMPT = "你是一个专业的学术笔记生成助手。请根据提供的文档内容，生成结构化、易于理解的学习笔记。"

# 动态导入 API 客户端
def get_api_client():
    """动态导入API客户端"""
    try:
        # 添加项目根目录到Python路径
        project_root = Path(__file__).parent.parent.parent
        sys.path.append(str(project_root))
        
        from api_client import APIClient
        from config import API_KEY, BASE_URL, DEFAULT_MODEL
        
        return APIClient(
            api_key=API_KEY,
            base_url=BASE_URL,
            default_model=DEFAULT_MODEL
        )
    except ImportError as e:
        print(f"Warning: API配置文件未找到 - {e}")
        return None
    except Exception as e:
        print(f"Warning: API客户端初始化失败 - {e}")
        return None

class NoteGenerator:
    """
    Django版本的笔记生成器
    根据JSON格式的文本内容，通过APIClient生成结构化的笔记
    """

    # 使用集中管理的系统提示词
    SYSTEM_PROMPT = NOTE_GENERATION_SYSTEM_PROMPT

    def __init__(self):
        """初始化笔记生成器"""
        self.api_client = get_api_client()

    def generate_notes_streaming(self, json_file_path: str, output_dir: str = None) -> Dict[str, Any]:
        """流式生成笔记，返回生成器用于实时传输"""
        try:
            # 创建输出目录
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            if output_dir is None:
                output_dir = "media/output"  # 默认路径，但应该由调用者指定用户特定路径

            notes_output_path = Path(output_dir) / timestamp

            notes_output_path.mkdir(parents=True, exist_ok=True)
            
            # 提取文本内容和图片信息
            extracted_data = self._extract_text_from_json(json_file_path, str(notes_output_path))
            text_content = extracted_data["text_content"]
            images_info = extracted_data["images_info"]
            
            if not text_content.strip():
                yield {"type": "error", "content": "JSON文件中没有找到文本内容"}
                return
            
            # 构建图片信息部分
            images_section = ""
            if images_info:
                images_section = "\n\n可用图片信息：\n"
                for i, img in enumerate(images_info, 1):
                    images_section += f"{i}. 页面{img['page']} - 路径: {img['rel_path']}\n"
                    images_section += f"   描述: {img['caption']}\n"
            
            prompt = self.SYSTEM_PROMPT + images_section + "\n\n文本内容:\n" + text_content
            
            # 保存提取的文本内容和提示词
            init_path = notes_output_path / "extracted_content.txt"
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(text_content)
            
            prompt_path = notes_output_path / "full_prompt.txt"
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(prompt)
            
            # 检查API客户端是否可用
            if not self.api_client:
                yield {"type": "error", "content": "API客户端不可用"}
                return
            
            # 流式生成
            md_file_path = notes_output_path / "notes.md"
            
            yield {"type": "start", "content": "开始生成笔记..."}
            
            try:
                stream = self.api_client.client.chat.completions.create(
                    model=self.api_client.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50000,
                    temperature=0.5,
                    timeout=300,  # 增加到5分钟
                    stream=True,
                    stream_options={"include_usage": True}
                )
                
                with open(md_file_path, "w", encoding="utf-8") as f:
                    for chunk in stream:
                        content_piece = None
                        if hasattr(chunk, "choices") and chunk.choices:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content is not None:
                                content_piece = delta.content
                            elif isinstance(delta, dict) and "content" in delta and delta["content"] is not None:
                                content_piece = delta["content"]
                        
                        if content_piece:
                            f.write(content_piece)
                            f.flush()
                            yield {"type": "content", "content": content_piece}
                
                # 生成目录文件
                toc_content = self._generate_table_of_contents(str(md_file_path))
                toc_file_path = notes_output_path / "contents.md"
                with open(toc_file_path, "w", encoding="utf-8") as f:
                    f.write(toc_content)

                yield {
                    "type": "complete",
                    "content": "笔记生成完成！",
                    "file_path": str(md_file_path),
                    "output_dir": str(notes_output_path),
                    "toc_file_path": str(toc_file_path),
                    "toc_content": toc_content
                }
                
            except Exception as e:
                yield {"type": "error", "content": f"API调用失败: {str(e)}"}
                
        except Exception as e:
            yield {"type": "error", "content": f"笔记生成失败: {str(e)}"}

    def _generate_table_of_contents(self, md_file_path: str) -> str:
        """从Markdown文件生成目录"""
        try:
            # 尝试多种编码方式读取文件
            content = None
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']

            for encoding in encodings:
                try:
                    with open(md_file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return '# 📚 笔记目录\n\n无法读取文件内容'

            lines = content.split('\n')
            toc_lines = ['# 📚 笔记目录\n']

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

                if level > 6 or level == 0:  # Markdown最多支持6级标题
                    continue

                # 提取标题文本
                title = line[level:].strip()
                if not title:
                    continue

                # 清理标题文本，移除可能的特殊字符
                title = ''.join(char for char in title if ord(char) < 65536)  # 移除超出BMP的字符

                # 生成目录项 - 使用HTML格式以便更好的样式控制
                if level == 1:
                    toc_lines.append(f'<div class="toc-level-1">📖 {title}</div>')
                elif level == 2:
                    toc_lines.append(f'<div class="toc-level-2">📄 {title}</div>')
                elif level == 3:
                    toc_lines.append(f'<div class="toc-level-3">📝 {title}</div>')
                else:
                    indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * (level - 1)
                    toc_lines.append(f'<div class="toc-level-{level}">{indent}• {title}</div>')

            # 如果没有找到任何标题
            if len(toc_lines) == 1:
                toc_lines.append('- 未找到标题内容')

            # 添加生成时间
            from datetime import datetime
            toc_lines.append(f'\n---\n*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')

            return '\n'.join(toc_lines)

        except Exception as e:
            return f'# 📚 笔记目录\n\n生成目录时出错: {str(e)}'

    def _extract_text_from_json(self, json_file_path: str, md_dir: str = None) -> Dict[str, Any]:
        """从JSON文件中提取文本内容和图片信息"""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON文件格式不正确，应该是一个数组")

            pages_text: Dict[str, List[str]] = {}
            pages_figures: Dict[str, List[str]] = {}
            images_info: List[Dict[str, str]] = []

            for item in data:
                if not isinstance(item, dict):
                    continue

                if item.get("type") == "text" and "content" in item:
                    page = str(item.get("page", "unknown"))
                    content = item.get("content", "").strip()
                    if content:
                        if page not in pages_text:
                            pages_text[page] = []
                        pages_text[page].append(content)

                elif item.get("type") == "figure" and "path" in item:
                    page = str(item.get("page", "unknown"))
                    abs_path = item.get("path", "")
                    caption = item.get("caption", "")

                    # 生成相对于md文件的路径
                    rel_path = abs_path
                    if md_dir and os.path.isabs(abs_path):
                        rel_path = os.path.relpath(abs_path, md_dir).replace("\\", "/")

                    # 对于用户特定路径，需要特殊处理
                    # 如果路径包含 media/用户ID/uploads，转换为相对路径
                    if "media" in rel_path and "uploads" in rel_path:
                        # 提取 uploads 后面的部分
                        uploads_index = rel_path.find("uploads")
                        if uploads_index != -1:
                            # 从 uploads 开始的路径部分
                            uploads_part = rel_path[uploads_index:]
                            # 生成相对于笔记输出目录的路径
                            rel_path = f"../../{uploads_part}"

                    images_info.append({"page": page, "abs_path": abs_path, "rel_path": rel_path, "caption": caption})
                    if page not in pages_figures:
                        pages_figures[page] = []
                    pages_figures[page].append(f"[图片] 路径: {rel_path}\n描述: {caption}")

            def page_sort_key(page_str):
                try:
                    return int(page_str)
                except (ValueError, TypeError):
                    return float('inf')

            organized_text = []
            all_pages = set(list(pages_text.keys()) + list(pages_figures.keys()))
            for page in sorted(all_pages, key=page_sort_key):
                page_content = "\n".join(pages_text.get(page, []))
                page_figures = "\n".join(pages_figures.get(page, []))
                if page_content:
                    page_content = page_content.strip()
                if page_figures:
                    page_figures = page_figures.strip()
                page_sections = []
                if page_content:
                    page_sections.append(page_content)
                if page_figures:
                    page_sections.append(page_figures)
                if page_sections:
                    page_text = f"=== 第{page}页 ===\n" + "\n\n".join(page_sections)
                    organized_text.append(page_text)

            return {
                "text_content": "\n\n".join(organized_text),
                "images_info": images_info
            }
        except Exception as e:
            raise e
