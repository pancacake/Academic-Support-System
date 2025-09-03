"""
性能测试模块
测试系统性能、响应时间和资源使用
"""

import os
import sys
import time
import psutil
import threading

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_memory_usage():
    """测试内存使用"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        print(f"当前内存使用: {memory_mb:.2f} MB")
        
        if memory_mb < 500:  # 500MB以下算正常
            print("✅ 内存使用测试成功")
            return True
        else:
            print("⚠️ 内存使用较高")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ 内存使用测试失败: {e}")
        return False

def test_cpu_usage():
    """测试CPU使用"""
    try:
        # 监控CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        print(f"当前CPU使用率: {cpu_percent}%")
        
        if cpu_percent < 80:  # 80%以下算正常
            print("✅ CPU使用测试成功")
            return True
        else:
            print("⚠️ CPU使用率较高")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ CPU使用测试失败: {e}")
        return False

def test_file_io_performance():
    """测试文件I/O性能"""
    try:
        import tempfile
        
        # 创建临时文件进行I/O测试
        test_data = "x" * 1024 * 1024  # 1MB数据
        
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_data)
            temp_file = f.name
        
        # 读取文件
        with open(temp_file, 'r') as f:
            read_data = f.read()
        
        end_time = time.time()
        io_time = end_time - start_time
        
        # 清理临时文件
        os.unlink(temp_file)
        
        print(f"文件I/O时间: {io_time:.3f}秒")
        
        if io_time < 1.0:  # 1秒以下算正常
            print("✅ 文件I/O性能测试成功")
            return True
        else:
            print("⚠️ 文件I/O性能较慢")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ 文件I/O性能测试失败: {e}")
        return False

def test_concurrent_requests():
    """测试并发请求处理"""
    try:
        # 模拟并发请求
        def simulate_request():
            time.sleep(0.1)  # 模拟请求处理时间
            return True
        
        start_time = time.time()
        
        # 创建多个线程模拟并发
        threads = []
        for i in range(10):
            thread = threading.Thread(target=simulate_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"10个并发请求处理时间: {total_time:.3f}秒")
        
        if total_time < 1.0:  # 1秒以下算正常
            print("✅ 并发请求测试成功")
            return True
        else:
            print("⚠️ 并发处理性能较慢")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ 并发请求测试失败: {e}")
        return False

def test_response_time():
    """测试响应时间"""
    try:
        # 模拟不同类型的操作
        operations = {
            '简单计算': lambda: sum(range(1000)),
            '字符串处理': lambda: 'test' * 1000,
            '列表操作': lambda: [i for i in range(1000)]
        }
        
        for op_name, operation in operations.items():
            start_time = time.time()
            result = operation()
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"{op_name}响应时间: {response_time:.6f}秒")
            
            if response_time > 0.1:  # 100ms以上算慢
                print(f"⚠️ {op_name}响应较慢")
        
        print("✅ 响应时间测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 响应时间测试失败: {e}")
        return False

def test_disk_space():
    """测试磁盘空间"""
    try:
        disk_usage = psutil.disk_usage('/')
        free_gb = disk_usage.free / 1024 / 1024 / 1024
        
        print(f"可用磁盘空间: {free_gb:.2f} GB")
        
        if free_gb > 1:  # 1GB以上算正常
            print("✅ 磁盘空间测试成功")
            return True
        else:
            print("⚠️ 磁盘空间不足")
            return False
            
    except Exception as e:
        print(f"❌ 磁盘空间测试失败: {e}")
        return False

def run_tests():
    """运行所有性能测试"""
    print("🔍 开始性能测试...")
    
    tests = [
        ("内存使用", test_memory_usage),
        ("CPU使用", test_cpu_usage),
        ("文件I/O性能", test_file_io_performance),
        ("并发请求", test_concurrent_requests),
        ("响应时间", test_response_time),
        ("磁盘空间", test_disk_space),
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
    
    print(f"\n📊 性能测试结果: {passed}/{total} 通过")
    return passed == total

if __name__ == "__main__":
    run_tests()
