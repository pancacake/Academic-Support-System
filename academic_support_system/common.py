# utils/common.py
import os
import json
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def ensure_output_dirs(username: str = None):
    """
    确保输出目录存在
    Args:
        username: 用户名，如果提供则创建用户特定的目录
    """
    if username:
        # 用户特定的输出目录
        user_json_dir = os.path.join(PROJECT_ROOT, "output", username, "json")
        user_images_dir = os.path.join(PROJECT_ROOT, "output", username, "images")
        os.makedirs(user_json_dir, exist_ok=True)
        os.makedirs(user_images_dir, exist_ok=True)
        return user_json_dir
    else:
        # 兼容旧逻辑，创建通用输出目录
        os.makedirs(os.path.join(PROJECT_ROOT, "output/json"), exist_ok=True)
        os.makedirs(os.path.join(PROJECT_ROOT, "output/images"), exist_ok=True)
        return os.path.join(PROJECT_ROOT, "output/json")

def save_json(data, filename):
    """
    将数据保存为 JSON 文件
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_json_output(source_file_path, json_path, username):
    """
    注册JSON输出到用户特定的index.json文件
    Args:
        source_file_path: 源文件路径
        json_path: JSON文件路径
        username: 用户名
    """
    # 用户特定的index.json路径
    user_json_dir = os.path.join(PROJECT_ROOT, "output", username, "json")
    index_file = os.path.join(user_json_dir, "index.json")
    os.makedirs(user_json_dir, exist_ok=True)

    # 加载已有的用户特定索引
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            try:
                index_data = json.load(f)
            except Exception:
                index_data = []
    else:
        index_data = []

    # 获取文件大小
    file_size = os.path.getsize(source_file_path)
    file_size_mb = round(file_size / (1024 * 1024), 2)
    file_size_str = f"{file_size_mb} MB"

    # 提取信息
    record = {
        "file_name": os.path.basename(source_file_path),
        "json_path": json_path,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file_size": file_size_str
    }

    # 添加到用户特定的索引中
    index_data.append(record)

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False) 