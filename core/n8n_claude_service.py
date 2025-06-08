#!/usr/bin/env python3
"""
🧠 N8N Claude Service
AI-сервис для генерации n8n workflow на основе описания бизнес-процессов
Адаптированная версия Claude Service специально для n8n
"""

import os
import json
from typing import Dict, List, Optional, Any
import anthropic
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from n8n_knowledge_base import N8NKnowledgeBase

class N8NClaudeService:
    """Claude AI сервис для генерации n8n workflow"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('CLAUDE_API_KEY', 'your_claude_api_key_here')
        )
        self.model = "claude-sonnet-4-20250514"
        self.knowledge_base = N8NKnowledgeBase()
        
    def generate_workflow(self, description: str, params: Dict = None) -> Dict:
        """Генерация n8n workflow из описания"""
        
        if params is None:
            params = {}
        
        # Создаем контекст для Claude
        context = self._create_context(description, params)
        
        # Генерируем промпт
        prompt = self._create_n8n_prompt(description, context)
        
        try:
            # Запрос к Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Парсим ответ
            workflow_json = self._parse_claude_response(response.content[0].text)
            
            # Валидируем workflow
            validated_workflow = self._validate_workflow(workflow_json)
            
            return {
                "status": "success",
                "workflow": validated_workflow,
                "description": description,
                "params": params,
                "claude_response": response.content[0].text[:500] + "..." if len(response.content[0].text) > 500 else response.content[0].text
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка генерации workflow: {str(e)}",
                "description": description
            }
    
    def _create_context(self, description: str, params: Dict) -> Dict:
        """Создание контекста для генерации"""
        
        # Анализируем описание для предложения паттерна
        suggested_pattern = self.knowledge_base.suggest_workflow_pattern(description)
        
        # Определяем сложность
        complexity = params.get('complexity', 'Средняя')
        
        # Определяем необходимые категории nodes
        node_categories = self._analyze_required_nodes(description)
        
        return {
            "complexity": complexity,
            "suggested_pattern": suggested_pattern,
            "node_categories": node_categories,
            "available_nodes": list(self.knowledge_base.nodes.keys()),
            "workflow_patterns": self.knowledge_base.workflow_patterns
        }
    
    def _analyze_required_nodes(self, description: str) -> List[str]:
        """Анализ необходимых типов nodes на основе описания"""
        description_lower = description.lower()
        required_categories = []
        
        # Триггеры
        if any(word in description_lower for word in ['webhook', 'получать', 'принимать', 'запрос']):
            required_categories.append('webhook')
        
        if any(word in description_lower for word in ['каждый', 'периодически', 'час', 'день', 'расписание']):
            required_categories.append('schedule')
        
        # HTTP запросы
        if any(word in description_lower for word in ['api', 'запрос', 'данные', 'получить']):
            required_categories.append('http')
        
        # Google сервисы
        if any(word in description_lower for word in ['google', 'sheets', 'таблица', 'gmail', 'email']):
            required_categories.append('google')
        
        # Коммуникации
        if any(word in description_lower for word in ['slack', 'уведомление', 'сообщение']):
            required_categories.append('communication')
        
        # Обработка данных
        if any(word in description_lower for word in ['обработать', 'изменить', 'добавить', 'условие']):
            required_categories.append('processing')
        
        return required_categories
    
    def _create_n8n_prompt(self, description: str, context: Dict) -> str:
        """Создание промпта для Claude специально для n8n"""
        
        suggested_pattern = context.get('suggested_pattern')
        pattern_info = ""
        if suggested_pattern:
            pattern_info = f"""
Рекомендуемый паттерн workflow: {suggested_pattern['description']}
Nodes в паттерне: {suggested_pattern['nodes']}
Connections: {suggested_pattern['connections']}
"""
        
        available_nodes_info = "\n".join([
            f"- {node}: {self.knowledge_base.nodes[node]['display_name']} - {self.knowledge_base.nodes[node]['description']}"
            for node in context['available_nodes'][:10]  # Показываем первые 10
        ])
        
        prompt = f"""
Ты эксперт по n8n - платформе автоматизации workflow. Создай РАБОЧИЙ n8n workflow на основе описания бизнес-процесса.

ОПИСАНИЕ ПРОЦЕССА:
{description}

КОНТЕКСТ:
- Сложность: {context['complexity']}
- Требуемые категории nodes: {context['node_categories']}
{pattern_info}

ДОСТУПНЫЕ N8N NODES (используй ТОЛЬКО эти):
{available_nodes_info}

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Используй ТОЛЬКО реальные n8n node types из списка выше
2. Создай корректную структуру n8n workflow JSON
3. Укажи правильные connections между nodes
4. Добавь реалистичные параметры для каждого node
5. Включи position координаты для визуального отображения
6. НЕ используй вымышленные или несуществующие nodes

СТРУКТУРА WORKFLOW:
```json
{{
  "name": "Название workflow",
  "active": false,
  "nodes": [
    {{
      "id": "1",
      "name": "Node Name",
      "type": "n8n-nodes-base.nodetype",
      "typeVersion": 1,
      "position": [100, 200],
      "parameters": {{
        // реальные параметры node
      }}
    }}
  ],
  "connections": {{
    "Node Name": {{
      "main": [[{{
        "node": "Next Node Name",
        "type": "main",
        "index": 0
      }}]]
    }}
  }},
  "settings": {{}},
  "staticData": {{}}
}}
```

ВАЖНО:
- Каждый node должен иметь уникальный id
- Connections используют имена nodes, не id
- Position должны быть логично расположены (100px между nodes)
- Parameters должны соответствовать реальным параметрам n8n nodes

Создай workflow который ТОЧНО БУДЕТ РАБОТАТЬ в n8n!
"""
        
        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """Парсинг ответа Claude для извлечения JSON workflow"""
        
        # Ищем JSON блок в ответе
        start_markers = ['```json', '```', '{']
        end_markers = ['```', '}']
        
        # Находим начало JSON
        start_pos = -1
        for marker in start_markers:
            pos = response_text.find(marker)
            if pos != -1:
                start_pos = pos + len(marker)
                break
        
        if start_pos == -1:
            # Если нет маркеров, ищем первую открывающую скобку
            start_pos = response_text.find('{')
        
        # Находим конец JSON
        end_pos = len(response_text)
        if '```' in response_text[start_pos:]:
            end_pos = response_text.find('```', start_pos)
        else:
            # Ищем последнюю закрывающую скобку
            end_pos = response_text.rfind('}') + 1
        
        if start_pos == -1 or end_pos == -1:
            raise ValueError("Не удалось найти JSON в ответе Claude")
        
        json_text = response_text[start_pos:end_pos].strip()
        
        # Очищаем от возможных артефактов
        if json_text.startswith('json\n'):
            json_text = json_text[5:]
        
        try:
            workflow_json = json.loads(json_text)
            return workflow_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Невалидный JSON от Claude: {str(e)}\nJSON: {json_text[:200]}...")
    
    def _validate_workflow(self, workflow: Dict) -> Dict:
        """Валидация сгенерированного workflow"""
        
        # Проверяем обязательные поля
        required_fields = ['name', 'nodes', 'connections']
        for field in required_fields:
            if field not in workflow:
                workflow[field] = self._get_default_value(field)
        
        # Валидируем nodes
        if not isinstance(workflow['nodes'], list):
            workflow['nodes'] = []
        
        validated_nodes = []
        for i, node in enumerate(workflow['nodes']):
            validated_node = self._validate_node(node, i)
            validated_nodes.append(validated_node)
        
        workflow['nodes'] = validated_nodes
        
        # Валидируем connections
        workflow['connections'] = self._validate_connections(
            workflow.get('connections', {}), 
            [node['name'] for node in validated_nodes]
        )
        
        # Добавляем поля по умолчанию
        workflow.setdefault('active', False)
        workflow.setdefault('settings', {})
        workflow.setdefault('staticData', {})
        
        return workflow
    
    def _validate_node(self, node: Dict, index: int) -> Dict:
        """Валидация отдельного node"""
        
        validated_node = {
            "id": node.get('id', str(index + 1)),
            "name": node.get('name', f"Node {index + 1}"),
            "type": node.get('type', 'n8n-nodes-base.set'),
            "typeVersion": node.get('typeVersion', 1),
            "position": node.get('position', [100 + index * 200, 200]),
            "parameters": node.get('parameters', {})
        }
        
        # Проверяем что node type существует в базе знаний
        if validated_node['type'] not in self.knowledge_base.nodes:
            # Заменяем на существующий node
            validated_node['type'] = 'n8n-nodes-base.set'
            validated_node['name'] = f"Set {index + 1}"
        
        return validated_node
    
    def _validate_connections(self, connections: Dict, node_names: List[str]) -> Dict:
        """Валидация connections между nodes"""
        
        validated_connections = {}
        
        for source_node, targets in connections.items():
            if source_node in node_names:
                validated_connections[source_node] = targets
        
        return validated_connections
    
    def _get_default_value(self, field: str) -> Any:
        """Получение значения по умолчанию для поля"""
        
        defaults = {
            'name': 'Generated Workflow',
            'nodes': [],
            'connections': {},
            'active': False,
            'settings': {},
            'staticData': {}
        }
        
        return defaults.get(field, None)


# Функция тестирования
def test_n8n_claude_service():
    """Тестирование N8N Claude Service"""
    
    print("🧠 Тестирование N8N Claude Service...")
    
    service = N8NClaudeService()
    
    # Тестовые описания
    test_cases = [
        {
            "description": "При получении webhook отправить уведомление в Slack",
            "params": {"complexity": "Простая"}
        },
        {
            "description": "Каждый час получать данные из API и сохранять в Google Sheets",
            "params": {"complexity": "Средняя"}
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📝 Тест {i+1}: {test_case['description']}")
        
        result = service.generate_workflow(
            test_case['description'], 
            test_case['params']
        )
        
        if result['status'] == 'success':
            workflow = result['workflow']
            print(f"✅ Workflow создан: {workflow['name']}")
            print(f"🔧 Nodes: {len(workflow['nodes'])}")
            print(f"🔗 Connections: {len(workflow['connections'])}")
            
            # Сохраняем результат
            output_path = f"/Users/hdv_1987/Desktop/Projects/N8N-Agent/examples/test_workflow_{i+1}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"💾 Сохранен: {output_path}")
        else:
            print(f"❌ Ошибка: {result['message']}")

if __name__ == "__main__":
    test_n8n_claude_service()
