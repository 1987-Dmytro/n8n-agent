#!/usr/bin/env python3
"""
🔍 Диагностика проблемы создания workflow
"""

import sys
import os
import json
sys.path.append('/Users/hdv_1987/Desktop/Projects/N8N-Agent/core')

from n8n_claude_service_mock import N8NClaudeServiceMock
from n8n_production_client import N8NProductionClient

def diagnose_workflow_issue():
    """Диагностика проблемы с созданием workflow"""
    
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМЫ СОЗДАНИЯ WORKFLOW")
    print("=" * 60)
    
    # 1. Генерируем workflow через Mock Claude
    print("\n1️⃣ Генерация workflow через Mock Claude...")
    mock_claude = N8NClaudeServiceMock()
    
    description = "При получении webhook отправить уведомление в Slack с информацией о событии"
    result = mock_claude.generate_workflow(description)
    
    workflow_data = result['workflow']
    
    print(f"✅ Workflow сгенерирован: {workflow_data['name']}")
    print(f"🔧 Nodes: {len(workflow_data.get('nodes', []))}")
    print(f"🔗 Connections: {len(workflow_data.get('connections', {}))}")
    
    # Сохраняем для анализа
    with open('/Users/hdv_1987/Desktop/Projects/N8N-Agent/debug_workflow.json', 'w') as f:
        json.dump(workflow_data, f, indent=2)
    
    print("💾 Workflow сохранен в debug_workflow.json")
    
    # 2. Анализируем структуру
    print(f"\n2️⃣ Анализ структуры workflow...")
    
    required_fields = ['name', 'nodes', 'connections', 'settings', 'staticData']
    missing_fields = [field for field in required_fields if field not in workflow_data]
    
    if missing_fields:
        print(f"❌ Отсутствуют поля: {missing_fields}")
    else:
        print("✅ Все обязательные поля присутствуют")
    
    # Проверяем nodes
    if 'nodes' in workflow_data:
        nodes = workflow_data['nodes']
        print(f"📊 Анализ {len(nodes)} nodes:")
        
        for i, node in enumerate(nodes):
            node_fields = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters']
            node_missing = [field for field in node_fields if field not in node]
            
            if node_missing:
                print(f"   ❌ Node {i+1}: отсутствуют поля {node_missing}")
            else:
                print(f"   ✅ Node {i+1}: {node.get('name')} ({node.get('type')})")
    
    # 3. Пробуем создать в n8n с детальной диагностикой
    print(f"\n3️⃣ Попытка создания в n8n с диагностикой...")
    
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTVhZTQ3YS1hZDNmLTQ1OTYtYjE5OS05ZjA4MTE2M2M5NGQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ5MzY4Njg0LCJleHAiOjE3NTE5NDcyMDB9.bvYcgPwSgZA1GEfIuBSkQ1Kv3imRu38JGdkQnEJ18VM"
    client = N8NProductionClient(api_key)
    
    create_result = client.create_workflow(workflow_data)
    
    if create_result['status'] == 'success':
        print(f"✅ Workflow успешно создан!")
        print(f"🆔 ID: {create_result['id']}")
        print(f"🔗 URL: {create_result['url']}")
    else:
        print(f"❌ Ошибка создания: {create_result['message']}")
        print(f"📝 Код ошибки: {create_result.get('status_code', 'unknown')}")
        print(f"📄 Ответ сервера: {create_result.get('response', 'Нет ответа')}")
        
        # Попробуем упрощенную версию
        print(f"\n4️⃣ Пробуем упрощенную версию workflow...")
        
        simple_workflow = {
            "name": "Debug Simple Test",
            "nodes": [
                {
                    "id": "1",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "typeVersion": 1,
                    "position": [100, 200],
                    "parameters": {}
                }
            ],
            "connections": {},
            "settings": {},
            "staticData": {}
        }
        
        simple_result = client.create_workflow(simple_workflow)
        
        if simple_result['status'] == 'success':
            print(f"✅ Упрощенный workflow создан!")
            print(f"🎯 Проблема в сложности структуры Mock workflow")
        else:
            print(f"❌ Даже упрощенный не работает: {simple_result['message']}")

if __name__ == "__main__":
    diagnose_workflow_issue()
