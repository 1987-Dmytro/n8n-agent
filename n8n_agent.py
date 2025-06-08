#!/usr/bin/env python3
"""
🎯 N8N-Agent CLI
Простой командный интерфейс для создания workflow в n8n
"""

import sys
import os
import argparse
from datetime import datetime

# Добавляем путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.n8n_main_service import N8NMainService

class N8NAgentCLI:
    """CLI интерфейс для N8N-Agent"""
    
    def __init__(self):
        self.service = None
    
    def create_workflow(self, description: str, complexity: str = "Средняя", 
                       activate: bool = False, use_mock: bool = None) -> None:
        """Создание workflow через CLI"""
        
        print("🚀 N8N-AGENT v1.0 - AI WORKFLOW CREATOR")
        print("=" * 60)
        
        # Автоматическое определение режима если не указан
        if use_mock is None:
            claude_api_key = os.getenv('CLAUDE_API_KEY')
            use_mock = not claude_api_key or claude_api_key == 'your_claude_api_key_here'
        
        # Инициализируем сервис
        self.service = N8NMainService(use_mock_claude=use_mock)
        
        # Параметры создания
        params = {
            "complexity": complexity,
            "auto_activate": activate
        }
        
        print(f"\n📝 Описание: {description}")
        print(f"⚙️ Сложность: {complexity}")
        print(f"⚡ Активация: {'Да' if activate else 'Нет'}")
        print(f"🧠 Режим: {'Mock Claude' if use_mock else 'Real Claude'}")
        
        # Создаем workflow
        result = self.service.create_workflow_from_description(description, params)
        
        # Выводим результат
        self._display_result(result)
    
    def _display_result(self, result: dict) -> None:
        """Отображение результата создания workflow"""
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print("=" * 40)
        
        if result['status'] == 'success':
            workflow = result['workflow']
            
            print(f"✅ УСПЕХ! Workflow создан")
            print(f"📋 Название: {workflow['name']}")
            print(f"🆔 ID: {workflow['id']}")
            print(f"🔗 URL: {workflow['url']}")
            print(f"🔧 Nodes: {workflow['nodes_count']}")
            print(f"🔗 Connections: {workflow['connections_count']}")
            print(f"⚡ Активен: {'Да' if workflow['active'] else 'Нет'}")
            
            print(f"\n🎯 ГОТОВО К ИСПОЛЬЗОВАНИЮ!")
            print(f"👉 Откройте: {workflow['url']}")
            
            # Если есть webhook, показываем URL
            if 'webhook' in result.get('generated_data', {}).get('nodes', [{}])[0].get('type', ''):
                webhook_path = result['generated_data']['nodes'][0]['parameters'].get('path', 'webhook')
                webhook_url = f"http://localhost:5678/webhook/{webhook_path}"
                print(f"🌐 Webhook URL: {webhook_url}")
            
        else:
            print(f"❌ ОШИБКА: {result['message']}")
            print(f"📍 Этап: {result.get('stage', 'unknown')}")
    
    def list_examples(self) -> None:
        """Показать примеры описаний для workflow"""
        
        examples = [
            {
                "description": "При получении webhook отправить уведомление в Slack",
                "complexity": "Простая",
                "result": "Webhook → Set Data → Slack"
            },
            {
                "description": "Каждый час получать данные о погоде и сохранять в Google Sheets",
                "complexity": "Средняя", 
                "result": "Schedule → HTTP Request → Google Sheets"
            },
            {
                "description": "При получении email с вложением сохранить файл и уведомить команду",
                "complexity": "Сложная",
                "result": "Email Trigger → File Processing → Notifications"
            }
        ]
        
        print("📚 ПРИМЕРЫ ОПИСАНИЙ ДЛЯ WORKFLOW")
        print("=" * 50)
        
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. {example['description']}")
            print(f"   Сложность: {example['complexity']}")
            print(f"   Результат: {example['result']}")
        
        print(f"\n💡 СОВЕТЫ ПО ОПИСАНИЮ:")
        print("• Укажите триггер (webhook, расписание, email)")
        print("• Опишите действия (получить, обработать, отправить)")
        print("• Укажите назначение (Slack, Sheets, email)")
        print("• Используйте простой русский язык")

def main():
    """Главная функция CLI"""
    
    parser = argparse.ArgumentParser(
        description="N8N-Agent v1.0 - Создание workflow в n8n по описанию",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Создать простой workflow
  python3 n8n_agent.py "При получении webhook отправить в Slack"
  
  # Создать со сложностью и активацией
  python3 n8n_agent.py "Каждый час синхронизировать данные" --complexity Сложная --activate
  
  # Показать примеры
  python3 n8n_agent.py --examples
  
  # Использовать реальный Claude (если есть API ключ)
  export CLAUDE_API_KEY=your_api_key
  python3 n8n_agent.py "Обработать заказы и отправить в CRM"
        """
    )
    
    parser.add_argument(
        'description', 
        nargs='?',
        help='Описание бизнес-процесса для создания workflow'
    )
    
    parser.add_argument(
        '--complexity', '-c',
        choices=['Простая', 'Средняя', 'Сложная'],
        default='Средняя',
        help='Сложность workflow (по умолчанию: Средняя)'
    )
    
    parser.add_argument(
        '--activate', '-a',
        action='store_true',
        help='Активировать workflow после создания'
    )
    
    parser.add_argument(
        '--mock', '-m',
        action='store_true',
        help='Принудительно использовать Mock Claude (без API)'
    )
    
    parser.add_argument(
        '--examples', '-e',
        action='store_true',
        help='Показать примеры описаний'
    )
    
    args = parser.parse_args()
    
    cli = N8NAgentCLI()
    
    if args.examples:
        cli.list_examples()
        return
    
    if not args.description:
        print("❌ Ошибка: Требуется описание workflow")
        print("💡 Используйте --examples для просмотра примеров")
        print("💡 Или укажите описание: python3 n8n_agent.py 'Ваше описание'")
        return
    
    cli.create_workflow(
        description=args.description,
        complexity=args.complexity,
        activate=args.activate,
        use_mock=args.mock
    )

if __name__ == "__main__":
    main()
