"""
统一的出题服务
"""
import json
import logging
from typing import Dict, List, Any, Optional
from .unified_api_client import unified_client
from prompts import (
    MULTIPLE_CHOICE_GENERATION_PROMPT,
    FILL_IN_BLANK_GENERATION_PROMPT,
    TRUE_FALSE_GENERATION_PROMPT,
    SHORT_ANSWER_GENERATION_PROMPT,
    ANSWER_REPORT_GENERATION_PROMPT
)
from .error_handler import error_handler

logger = logging.getLogger(__name__)

class QuestionService:
    """统一的出题服务"""
    
    def __init__(self):
        self.client = unified_client
    
    def generate_questions(
        self,
        notes_content: str,
        question_types: Dict[str, Dict[str, Any]],
        user_preferences: str = "",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成题目的主要方法
        
        Args:
            notes_content: 笔记内容
            question_types: 题目类型配置 {'multipleChoice': {'name': '选择题', 'count': 5}}
            user_preferences: 用户偏好
            user_id: 用户ID
        
        Returns:
            包含生成结果的字典
        """
        try:
            # 验证输入参数
            if not notes_content or notes_content.strip() == "":
                return error_handler.handle_validation_error("笔记内容不能为空", "笔记内容")

            if not question_types or len(question_types) == 0:
                return error_handler.handle_validation_error("必须选择至少一种题目类型", "题目类型")

            if not self.client.is_available():
                logger.warning("API不可用，使用备用方案")
                fallback_result = self._generate_fallback_questions(question_types, notes_content)
                fallback_result['message'] = "AI服务暂时不可用，已为您生成示例题目"
                return fallback_result

            questions = []

            # 为每种题型分别生成题目
            for type_key, type_info in question_types.items():
                type_name = type_info['name']
                count = type_info['count']

                if count <= 0:
                    continue

                logger.info(f"正在生成{count}道{type_name}")

                # 获取对应的提示词模板
                prompt_template = self._get_prompt_template(type_name)
                if not prompt_template:
                    logger.warning(f"未找到{type_name}的提示词模板，跳过")
                    continue

                # 生成该类型的题目
                type_questions = self._generate_questions_by_type(
                    prompt_template, type_name, count, notes_content, user_preferences
                )
                questions.extend(type_questions)

            if not questions:
                return error_handler.handle_business_error("未能生成任何题目，请检查笔记内容或重试")

            # 生成题目总结
            summary = self._generate_questions_summary(questions, question_types)

            return error_handler.create_success_response({
                'questions': questions,
                'total_count': len(questions),
                'questions_summary': summary
            }, f"成功生成了{len(questions)}道题目")

        except Exception as e:
            logger.error(f"生成题目失败: {e}")
            # 尝试提供备用方案
            try:
                fallback_result = self._generate_fallback_questions(question_types, notes_content)
                fallback_result['error'] = f"生成过程中出现问题，已提供备用题目: {str(e)}"
                fallback_result['success'] = False
                return fallback_result
            except:
                return error_handler.handle_system_error(e, "题目生成")
    
    def _get_prompt_template(self, question_type: str) -> Optional[str]:
        """获取题型对应的提示词模板"""
        prompt_mapping = {
            '选择题': MULTIPLE_CHOICE_GENERATION_PROMPT,
            '填空题': FILL_IN_BLANK_GENERATION_PROMPT,
            '判断题': TRUE_FALSE_GENERATION_PROMPT,
            '解答题': SHORT_ANSWER_GENERATION_PROMPT
        }
        return prompt_mapping.get(question_type)
    
    def _generate_questions_by_type(
        self,
        prompt_template: str,
        question_type: str,
        count: int,
        notes_content: str,
        user_preferences: str
    ) -> List[Dict[str, Any]]:
        """为特定题型生成题目"""
        questions = []
        
        for i in range(count):
            try:
                # 构建完整提示词
                full_prompt = self._build_full_prompt(
                    prompt_template, question_type, notes_content, 
                    user_preferences, i, count
                )
                
                # 调用API生成题目
                logger.info(f"开始生成第{i+1}道{question_type}...")
                try:
                    response = self.client.call_api(full_prompt)
                    logger.info(f"API调用成功，响应长度: {len(response)}")
                except Exception as api_error:
                    logger.error(f"API调用失败: {type(api_error).__name__}: {api_error}")
                    raise api_error

                # 解析响应
                question_data = self._parse_question_response(response, question_type)
                
                if question_data:
                    questions.append(question_data)
                else:
                    # 解析失败，使用备用题目
                    fallback_question = self._create_fallback_question(question_type, i + 1)
                    questions.append(fallback_question)
                    
            except Exception as e:
                logger.error(f"生成第{i+1}道{question_type}失败: {e}")
                # 添加备用题目
                fallback_question = self._create_fallback_question(question_type, i + 1)
                questions.append(fallback_question)
        
        return questions
    
    def _build_full_prompt(
        self,
        template: str,
        question_type: str,
        notes_content: str,
        user_preferences: str,
        current_index: int,
        total_count: int
    ) -> str:
        """构建完整的提示词"""
        # 获取多样化的内容片段
        content_section = self._get_diverse_content_section(notes_content, current_index, total_count)
        
        # 多样性指导
        diversity_instruction = f"""
请确保这道题目与之前生成的题目有所不同，关注不同的知识点。
这是第{current_index + 1}道题目，共需要生成{total_count}道{question_type}。
"""
        
        # 用户偏好
        preference_text = f"\n用户偏好：{user_preferences}" if user_preferences else ""
        
        return f"""{template}

{diversity_instruction}

学习笔记内容：
{content_section}
{preference_text}

请基于以上笔记内容生成一道{question_type}。确保题目内容准确、有意义，并提供详细的解析。
请以JSON格式返回，包含以下字段：
- text: 题目内容
- type: 题目类型
- options: 选项列表（选择题和判断题需要）
- answer: 正确答案
- explanation: 详细解析
"""
    
    def _get_diverse_content_section(self, content: str, index: int, total: int) -> str:
        """获取多样化的内容片段"""
        if not content:
            return "暂无笔记内容"
        
        # 将内容分段，确保不同题目使用不同的内容片段
        content_length = len(content)
        section_size = min(1000, content_length // max(total, 1))
        
        start_pos = (index * section_size) % max(content_length - section_size, 1)
        end_pos = min(start_pos + section_size, content_length)
        
        return content[start_pos:end_pos]
    
    def _parse_question_response(self, response: str, question_type: str) -> Optional[Dict[str, Any]]:
        """解析AI响应为题目数据"""
        try:
            # 清理响应内容
            response = response.strip()
            logger.info(f"尝试解析响应: {response[:200]}...")

            # 尝试多种JSON提取方法
            json_str = None
            import re

            # 方法1: 提取```json```包装的内容
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info("使用```json```格式提取")

            # 方法2: 提取{}包装的JSON
            if not json_str:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0).strip()
                    logger.info("使用{}格式提取")

            # 方法3: 直接使用响应内容
            if not json_str:
                json_str = response
                logger.info("直接使用响应内容")

            # 尝试解析JSON
            question_data = json.loads(json_str)

            # 验证和标准化数据
            return self._validate_and_normalize_question(question_data, question_type)

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 响应内容: {response[:200]}...")
            return self._create_fallback_question(question_type, 1)
        except Exception as e:
            logger.error(f"解析题目响应失败: {e}")
            return self._create_fallback_question(question_type, 1)
    
    def _validate_and_normalize_question(self, data: Dict[str, Any], question_type: str) -> Dict[str, Any]:
        """验证和标准化题目数据"""
        normalized = {
            'text': data.get('text', f'默认{question_type}题目'),
            'type': question_type,
            'answer': data.get('answer', '默认答案'),
            'explanation': data.get('explanation', '默认解析')
        }
        
        # 处理选项
        if question_type in ['选择题', '判断题']:
            if question_type == '判断题':
                normalized['options'] = ['A. 正确', 'B. 错误']
                # 标准化判断题答案
                if normalized['answer'] in ['对', '正确', 'True', 'true', '是']:
                    normalized['answer'] = 'A'
                elif normalized['answer'] in ['错', '错误', 'False', 'false', '否']:
                    normalized['answer'] = 'B'
            else:
                normalized['options'] = data.get('options', ['A. 选项1', 'B. 选项2', 'C. 选项3', 'D. 选项4'])
        
        return normalized

    def _create_fallback_question(self, question_type: str, index: int) -> Dict[str, Any]:
        """创建备用题目"""
        import random

        # 更丰富的备用题目模板
        fallback_templates = {
            '选择题': [
                {
                    'text': '根据学习内容，以下哪个概念最为重要？',
                    'options': ['A. 基础概念', 'B. 核心理论', 'C. 实践应用', 'D. 综合理解'],
                    'answer': 'B',
                    'explanation': '核心理论是学习的重点，需要深入理解。'
                },
                {
                    'text': '在学习过程中，哪种方法最有效？',
                    'options': ['A. 理论学习', 'B. 实践练习', 'C. 综合运用', 'D. 反复复习'],
                    'answer': 'C',
                    'explanation': '综合运用理论和实践是最有效的学习方法。'
                }
            ],
            '填空题': [
                {
                    'text': '学习的核心在于______和实践的结合。',
                    'answer': '理论',
                    'explanation': '理论与实践相结合是有效学习的关键。'
                },
                {
                    'text': '掌握知识需要通过______来加深理解。',
                    'answer': '练习',
                    'explanation': '通过练习可以加深对知识的理解和掌握。'
                }
            ],
            '判断题': [
                {
                    'text': '学习需要循序渐进，不能急于求成。',
                    'options': ['A. 正确', 'B. 错误'],
                    'answer': 'A',
                    'explanation': '学习确实需要循序渐进，这样才能打好基础。'
                },
                {
                    'text': '理论学习比实践应用更重要。',
                    'options': ['A. 正确', 'B. 错误'],
                    'answer': 'B',
                    'explanation': '理论和实践同样重要，需要相互结合。'
                }
            ],
            '解答题': [
                {
                    'text': '请说明有效学习的基本要素有哪些？',
                    'answer': '有效学习的基本要素包括：1. 明确的学习目标；2. 系统的知识结构；3. 适当的学习方法；4. 持续的练习和反思。',
                    'explanation': '这些要素相互配合，形成完整的学习体系。'
                }
            ]
        }

        # 随机选择一个模板
        templates = fallback_templates.get(question_type, fallback_templates['选择题'])
        fallback = random.choice(templates).copy()
        fallback['type'] = question_type

        # 添加题目编号
        fallback['text'] = f"[备用题目 {index}] {fallback['text']}"

        return fallback

    def _generate_fallback_questions(self, question_types: Dict[str, Dict[str, Any]], notes_content: str) -> Dict[str, Any]:
        """生成备用题目集合"""
        questions = []

        for type_key, type_info in question_types.items():
            type_name = type_info['name']
            count = type_info['count']

            for i in range(count):
                fallback_question = self._create_fallback_question(type_name, i + 1)
                questions.append(fallback_question)

        return {
            'success': True,
            'questions': questions,
            'total_count': len(questions),
            'questions_summary': f'生成了{len(questions)}道备用题目（API不可用）'
        }

    def _generate_questions_summary(self, questions: List[Dict[str, Any]], question_types: Dict[str, Dict[str, Any]]) -> str:
        """生成题目总结"""
        if not self.client.is_available():
            return self._generate_simple_summary(questions, question_types)

        try:
            # 构建题目信息
            questions_info = []
            for i, question in enumerate(questions, 1):
                questions_info.append(f"第{i}题（{question.get('type', '未知题型')}）：{question.get('text', '')[:50]}...")

            # 统计题型分布
            type_stats = {}
            for type_key, type_info in question_types.items():
                type_stats[type_info['name']] = type_info['count']

            prompt = f"""请为以下生成的题目集合写一段简明扼要的介绍，包括：
1. 题目数量和题型分布
2. 涵盖的主要知识点
3. 学习建议

题型分布：
{', '.join([f"{name} {count}道" for name, count in type_stats.items()])}

题目列表：
{chr(10).join(questions_info[:10])}  # 只显示前10题

请用简洁友好的语言，为学习者提供有用的指导。"""

            summary = self.client.call_api(prompt, max_tokens=500)
            return summary

        except Exception as e:
            logger.error(f"生成题目总结失败: {e}")
            return self._generate_simple_summary(questions, question_types)

    def _generate_simple_summary(self, questions: List[Dict[str, Any]], question_types: Dict[str, Dict[str, Any]]) -> str:
        """生成简单的题目总结"""
        total_count = len(questions)
        type_counts = {}

        for question in questions:
            q_type = question.get('type', '未知')
            type_counts[q_type] = type_counts.get(q_type, 0) + 1

        type_text = '、'.join([f"{count}道{q_type}" for q_type, count in type_counts.items()])

        return f"成功生成了{total_count}道题目，包括{type_text}。题目将在右侧逐一展示，请认真作答。"

# 全局服务实例
question_service = QuestionService()
