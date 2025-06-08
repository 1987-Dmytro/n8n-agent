#!/usr/bin/env python3
"""
🧪 Автоматическое тестирование N8N Main Service
"""

import sys
import os
sys.path.append('/Users/hdv_1987/Desktop/Projects/N8N-Agent/core')

from n8n_main_service import N8NMainService

def test_automatic():
    """Автоматическое тестирование Main Service"""
    
    print("🧪 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ N8N MAIN SERVICE")
    print("=" * 60)
    
    # Инициализируем сервис (Mock режим)
    service = N8NMainService(use_mock_claude=True)
    
    # Тестовый пример
    description = "При получении webhook отправить уведомление в Slack с информацией о событии"
    params = {"complexity": "Простая", "auto_activate": False}
    
    print(f"\n📝 Тестируем: {description}")
    
    # Создаем workflow
    result = service.create_workflow_from_description(description, params)
    
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"Статус: {result['status']}")
    
    if result['status'] == 'success':
        workflow = result['workflow']
        print(f"✅ Workflow создан: {workflow['name']}")
        print(f"🔗 URL: {workflow['url']}")
        print(f"🆔 ID: {workflow['id']}")
        print(f"🔧 Nodes: {workflow['nodes_count']}")
        print(f"🔗 Connections: {workflow['connections_count']}")
        print(f"⚡ Активен: {'Да' if workflow['active'] else 'Нет'}")
        
        print(f"\n🎉 ПОЛНЫЙ ПАЙПЛАЙН РАБОТАЕТ!")
        print(f"📋 От описания до готового workflow в n8n!")
        
        return True
    else:
        print(f"❌ Ошибка на этапе: {result.get('stage', 'unknown')}")
        print(f"📝 Сообщение: {result['message']}")
        
        return False

if __name__ == "__main__":
    success = test_automatic()
    if success:
        print(f"\n🏆 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print(f"\n❌ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
