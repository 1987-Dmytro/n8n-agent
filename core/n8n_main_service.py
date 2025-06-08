#!/usr/bin/env python3
"""
🎯 N8N Main Service
Центральный сервис для создания workflow от текстового описания до готового n8n workflow
"""

import os
import sys
import json
from typing import Dict, List, Optional
from datetime import datetime

# Добавляем путь для импорта наших модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from n8n_knowledge_base import N8NKnowledgeBase
from n8n_claude_service import N8NClaudeService
from n8n_claude_service_mock import N8NClaudeServiceMock
from n8n_production_client import N8NProductionClient

class N8NMainService:
    """Главный сервис N8N-Agent для создания workflow"""
    
    def __init__(self, use_mock_claude: bool = False):
        """
        Инициализация главного сервиса
        
        Args:
            use_mock_claude: Использовать mock версию Claude (для тестирования без API ключа)
        """
        self.use_mock_claude = use_mock_claude
        
        # Инициализируем компоненты
        self.knowledge_base = N8NKnowledgeBase()
        
        # Claude Service (реальный или mock)
        if use_mock_claude:
            self.claude_service = N8NClaudeServiceMock()
            print("🧪 Используется Mock Claude Service")
        else:
            self.claude_service = N8NClaudeService()
            print("🧠 Используется реальный Claude API")
        
        # N8N Production Client
        self.n8n_api_key = os.getenv('N8N_API_KEY') or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTVhZTQ3YS1hZDNmLTQ1OTYtYjE5OS05ZjA4MTE2M2M5NGQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ5MzY4Njg0LCJleHAiOjE3NTE5NDcyMDB9.bvYcgPwSgZA1GEfIuBSkQ1Kv3imRu38JGdkQnEJ18VM"
        self.n8n_client = N8NProductionClient(self.n8n_api_key)
        
        print("✅ N8N Main Service инициализирован")
    
    def create_workflow_from_description(self, description: str, params: Dict = None) -> Dict:
        """
        Создание workflow от описания до готового n8n workflow
        
        Args:
            description: Текстовое описание бизнес-процесса
            params: Дополнительные параметры (сложность, типы nodes и т.д.)
        
        Returns:
            Dict с результатом создания workflow
        """
        if params is None:
            params = {}
        
        print(f"\n🎯 СОЗДАНИЕ WORKFLOW ИЗ ОПИСАНИЯ")
        print(f"📝 Описание: {description}")
        print(f"⚙️ Параметры: {params}")
        print("=" * 60)
        
        try:
            # ЭТАП 1: Анализ описания и генерация workflow
            print("\n1️⃣ Генерация workflow через Claude AI...")
            
            claude_result = self.claude_service.generate_workflow(description, params)
            
            if claude_result['status'] != 'success':
                return {
                    "status": "error",
                    "stage": "claude_generation",
                    "message": f"Ошибка генерации Claude: {claude_result['message']}"
                }
            
            workflow_data = claude_result['workflow']
            print(f"✅ Workflow сгенерирован: {workflow_data['name']}")
            print(f"🔧 Nodes: {len(workflow_data['nodes'])}")
            print(f"🔗 Connections: {len(workflow_data['connections'])}")
            
            # ЭТАП 2: Создание workflow в n8n
            print("\n2️⃣ Создание workflow в n8n...")
            
            n8n_result = self.n8n_client.create_workflow(workflow_data)
            
            if n8n_result['status'] != 'success':
                return {
                    "status": "error", 
                    "stage": "n8n_creation",
                    "message": f"Ошибка создания в n8n: {n8n_result['message']}",
                    "generated_workflow": workflow_data
                }
            
            workflow_id = n8n_result['id']
            workflow_url = n8n_result['url']
            
            print(f"✅ Workflow создан в n8n!")
            print(f"🆔 ID: {workflow_id}")
            print(f"🔗 URL: {workflow_url}")
            
            # ЭТАП 3: Попытка активации (опционально)
            activation_result = None
            if params.get('auto_activate', False):
                print("\n3️⃣ Активация workflow...")
                activation_result = self.n8n_client.activate_workflow(workflow_id)
                
                if activation_result['status'] == 'success':
                    print("✅ Workflow активирован!")
                else:
                    print(f"⚠️ Проблема с активацией: {activation_result['message']}")
            
            # ЭТАП 4: Формирование итогового результата
            final_result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "description": description,
                "workflow": {
                    "id": workflow_id,
                    "name": workflow_data['name'],
                    "url": workflow_url,
                    "nodes_count": len(workflow_data['nodes']),
                    "connections_count": len(workflow_data['connections']),
                    "active": activation_result['status'] == 'success' if activation_result else False
                },
                "generated_data": workflow_data,
                "claude_response": claude_result.get('claude_response', ''),
                "n8n_response": n8n_result,
                "activation_result": activation_result
            }
            
            # Сохраняем результат
            self._save_result(final_result)
            
            print(f"\n🎉 WORKFLOW УСПЕШНО СОЗДАН!")
            print(f"📋 Детали сохранены в results/")
            
            return final_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "stage": "unexpected_error", 
                "message": f"Неожиданная ошибка: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"\n❌ ОШИБКА: {str(e)}")
            return error_result
    
    def _save_result(self, result: Dict) -> None:
        """Сохранение результата создания workflow"""
        
        # Создаем папку для результатов
        results_dir = "/Users/hdv_1987/Desktop/Projects/N8N-Agent/results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_name = result.get('workflow', {}).get('name', 'Unknown')
        safe_name = "".join(c for c in workflow_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{timestamp}_{safe_name.replace(' ', '_')}.json"
        
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Результат сохранен: {filepath}")
    
    def get_available_nodes(self) -> Dict:
        """Получение информации о доступных nodes"""
        
        return {
            "total_nodes": len(self.knowledge_base.nodes),
            "categories": self.knowledge_base.categories,
            "nodes": {
                name: {
                    "display_name": info['display_name'],
                    "description": info['description'],
                    "category": info['category']
                }
                for name, info in self.knowledge_base.nodes.items()
            }
        }
    
    def suggest_workflow_pattern(self, description: str) -> Optional[Dict]:
        """Предложение подходящего паттерна workflow"""
        return self.knowledge_base.suggest_workflow_pattern(description)
    
    def validate_description(self, description: str) -> Dict:
        """Валидация описания бизнес-процесса"""
        
        if not description or len(description.strip()) < 10:
            return {
                "valid": False,
                "message": "Описание слишком короткое. Минимум 10 символов."
            }
        
        # Простая проверка на наличие ключевых слов
        keywords = ['получать', 'отправлять', 'создавать', 'обрабатывать', 'когда', 'если']
        has_keywords = any(keyword in description.lower() for keyword in keywords)
        
        if not has_keywords:
            return {
                "valid": True,
                "message": "Описание принято, но рекомендуется добавить больше деталей о действиях.",
                "suggestions": [
                    "Укажите триггер (когда запускается процесс)",
                    "Опишите действия (что нужно сделать)",
                    "Уточните результат (куда отправлять данные)"
                ]
            }
        
        return {
            "valid": True,
            "message": "Описание подходит для создания workflow"
        }

def main():
    """Интерактивное тестирование Main Service"""
    
    print("🚀 ИНТЕРАКТИВНОЕ ТЕСТИРОВАНИЕ N8N MAIN SERVICE")
    print("=" * 60)
    
    # Проверяем наличие Claude API ключа
    claude_api_key = os.getenv('CLAUDE_API_KEY')
    use_mock = not claude_api_key or claude_api_key == 'your_claude_api_key_here'
    
    if use_mock:
        print("⚠️  Не найден Claude API ключ, используем Mock режим")
    else:
        print("✅ Claude API ключ найден, используем реальный Claude")
    
    # Инициализируем сервис
    service = N8NMainService(use_mock_claude=use_mock)
    
    # Тестовые примеры
    test_examples = [
        {
            "description": "При получении webhook отправить уведомление в Slack с информацией о событии",
            "params": {"complexity": "Простая", "auto_activate": False}
        },
        {
            "description": "Каждый час получать данные о погоде через API и сохранять в Google Sheets",
            "params": {"complexity": "Средняя", "auto_activate": False}
        }
    ]
    
    print(f"\n📋 Доступно {len(test_examples)} тестовых примеров:")
    for i, example in enumerate(test_examples, 1):
        print(f"{i}. {example['description']}")
    
    # Интерактивный выбор
    choice = input(f"\nВыберите пример (1-{len(test_examples)}) или введите 'custom' для своего описания: ").strip()
    
    if choice == 'custom':
        description = input("Введите описание бизнес-процесса: ").strip()
        params = {"complexity": "Средняя", "auto_activate": False}
    elif choice.isdigit() and 1 <= int(choice) <= len(test_examples):
        example = test_examples[int(choice) - 1]
        description = example['description']
        params = example['params']
    else:
        print("❌ Неверный выбор, используем первый пример")
        example = test_examples[0]
        description = example['description']
        params = example['params']
    
    # Создаем workflow
    result = service.create_workflow_from_description(description, params)
    
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"Статус: {result['status']}")
    
    if result['status'] == 'success':
        workflow = result['workflow']
        print(f"✅ Workflow создан: {workflow['name']}")
        print(f"🔗 URL: {workflow['url']}")
        print(f"🔧 Nodes: {workflow['nodes_count']}")
        print(f"⚡ Активен: {'Да' if workflow['active'] else 'Нет'}")
    else:
        print(f"❌ Ошибка: {result['message']}")

if __name__ == "__main__":
    main()
