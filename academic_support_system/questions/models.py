from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class GeneratedQuestion(models.Model):
    """存储生成的题目的数据库模型"""
    QUESTION_TYPES = [
        ('选择题', '选择题'),
        ('填空题', '填空题'),
        ('判断题', '判断题'),
        ('简答题', '简答题'),
        ('证明题', '证明题'),
    ]
    DIFFICULTY_LEVELS = [
        ('简单', '简单'),
        ('中等', '中等'),
        ('困难', '困难'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True)
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, verbose_name="题型")
    text = models.TextField(verbose_name="题目内容")
    options = models.JSONField(default=list, blank=True, verbose_name="选项（选择题专用）")
    answer = models.TextField(verbose_name="答案")
    difficulty = models.CharField(max_length=2, choices=DIFFICULTY_LEVELS, default='中等', verbose_name="难度")
    generated_at = models.DateTimeField(default=timezone.now, verbose_name="生成时间")
    json_file_path = models.CharField(max_length=255, verbose_name="对应JSON文件路径", blank=True)
    knowledge_point = models.TextField(verbose_name="考点", blank=True, null=True)
    explanation = models.TextField(verbose_name="解析", blank=True, null=True)

    def __str__(self):
        return f"{self.type}：{self.text[:30]}"

    class Meta:
        verbose_name = "生成的题目"
        verbose_name_plural = "生成的题目"


class UserAnswer(models.Model):
    """用户答题记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE, verbose_name="题目")
    user_answer = models.TextField(verbose_name="用户答案")
    is_correct = models.BooleanField(default=False, verbose_name="是否正确")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="答题时间")

    def __str__(self):
        return f"答题记录：{self.question.text[:20]}"

    class Meta:
        verbose_name = "答题记录"
        verbose_name_plural = "答题记录"


class QuestionSession(models.Model):
    """答题会话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True, verbose_name="会话ID")
    questions = models.ManyToManyField(GeneratedQuestion, verbose_name="题目列表")
    current_question_index = models.IntegerField(default=0, verbose_name="当前题目索引")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")

    def __str__(self):
        return f"答题会话：{self.session_id}"

    class Meta:
        verbose_name = "答题会话"
        verbose_name_plural = "答题会话"
