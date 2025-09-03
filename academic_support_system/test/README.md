# 学术支持系统测试套件

这是学术支持系统的综合测试套件，提供全面的功能测试、性能测试和集成测试。

## 📁 测试结构

```
test/
├── test_runner.py          # 主测试运行器
├── test_api_client.py      # API客户端测试
├── test_file_upload.py     # 文件上传测试
├── test_note_generation.py # 笔记生成测试
├── test_mindmap.py         # 思维导图测试
├── test_questions.py       # 出题功能测试
├── test_user_auth.py       # 用户认证测试
├── test_chat.py            # 聊天功能测试
├── test_database.py        # 数据库测试
├── test_frontend.py        # 前端功能测试
├── test_performance.py     # 性能测试
├── test_integration.py     # 集成测试
├── __init__.py             # 包初始化文件
└── README.md               # 本文件
```

## 🚀 快速开始

### 运行所有测试

```bash
cd academic_support_system
python test/test_runner.py
```

然后选择 `0` 运行所有测试。

### 运行单个测试模块

```bash
# 运行API客户端测试
python test/test_api_client.py

# 运行文件上传测试
python test/test_file_upload.py

# 运行笔记生成测试
python test/test_note_generation.py
```

### 交互式测试

```bash
python test/test_runner.py
```

然后根据菜单选择要运行的测试模块。

## 📋 测试模块详情

### 1. API客户端测试 (test_api_client.py)
- ✅ API客户端导入
- ✅ API客户端初始化
- ✅ 配置文件加载
- ✅ 简单API调用
- ✅ API响应时间
- ✅ 错误处理

### 2. 文件上传测试 (test_file_upload.py)
- ✅ 文件解析器导入
- ✅ 上传目录创建
- ✅ 文本文件处理
- ✅ 文件大小验证
- ✅ 文件类型验证
- ✅ 上传路径安全
- ✅ 旧文件清理

### 3. 笔记生成测试 (test_note_generation.py)
- ✅ 笔记生成器导入
- ✅ 提示词导入
- ✅ 输出目录创建
- ✅ 内容提取
- ✅ Markdown生成
- ✅ 文件保存
- ✅ 流式传输模拟
- ✅ 目录生成

### 4. 思维导图测试 (test_mindmap.py)
- ✅ 思维导图视图导入
- ✅ Markdown解析
- ✅ 思维导图结构
- ✅ JSON序列化
- ✅ 节点样式
- ✅ AI补全功能
- ✅ 布局算法
- ✅ 节点交互

### 5. 出题功能测试 (test_questions.py)
- ✅ 出题视图导入
- ✅ 题目提示词
- ✅ 题目类型
- ✅ 题目解析
- ✅ 回退题目

### 6. 用户认证测试 (test_user_auth.py)
- ✅ 用户模型导入
- ✅ 用户视图导入
- ✅ 会话管理
- ✅ 用户ID生成
- ✅ 游客模式
- ✅ 权限检查

### 7. 聊天功能测试 (test_chat.py)
- ✅ 聊天视图导入
- ✅ 消息处理
- ✅ @功能
- ✅ 修改确认

### 8. 数据库测试 (test_database.py)
- ✅ Django设置
- ✅ 数据库连接
- ✅ 模型导入
- ✅ 迁移状态

### 9. 前端功能测试 (test_frontend.py)
- ✅ 模板文件
- ✅ 静态文件
- ✅ JavaScript语法
- ✅ CSS结构
- ✅ 响应式设计
- ✅ 可访问性

### 10. 性能测试 (test_performance.py)
- ✅ 内存使用
- ✅ CPU使用
- ✅ 文件I/O性能
- ✅ 并发请求
- ✅ 响应时间
- ✅ 磁盘空间

### 11. 集成测试 (test_integration.py)
- ✅ 完整工作流程
- ✅ API集成
- ✅ 数据库集成
- ✅ 文件系统集成
- ✅ 用户会话集成
- ✅ 错误处理集成
- ✅ 性能集成

## 📊 测试报告

测试运行器会生成详细的测试报告，包括：
- 总测试数
- 通过/失败数量
- 成功率
- 详细的测试结果
- 测试完成时间

## 🔧 依赖要求

测试套件需要以下依赖：
- Django
- psutil (用于性能测试)
- 其他项目依赖

## 📝 添加新测试

要添加新的测试模块：

1. 在 `test/` 目录下创建新的测试文件
2. 实现 `run_tests()` 函数
3. 在 `test_runner.py` 中添加新模块
4. 更新本README文件

## 🐛 故障排除

如果测试失败，请检查：
1. Django环境是否正确配置
2. 数据库连接是否正常
3. 所有依赖是否已安装
4. API配置是否正确

## 📞 支持

如有问题，请联系开发团队或查看项目文档。
