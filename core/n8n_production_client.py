#!/usr/bin/env python3
"""
🚀 N8N Production API Client
Рабочий клиент для создания workflow в n8n через реальный API
"""

import requests
import json
from typing import Dict, List, Optional

class N8NProductionClient:
    """Production-ready клиент для n8n API"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:5678"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Создание workflow в n8n"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows",
                json=workflow_data
            )
            
            if response.status_code in [200, 201]:
                created_workflow = response.json()
                return {
                    "status": "success",
                    "workflow": created_workflow,
                    "id": created_workflow.get('id'),
                    "name": created_workflow.get('name'),
                    "url": f"{self.base_url}/workflow/{created_workflow.get('id')}",
                    "message": "Workflow создан успешно!"
                }
            else:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "message": f"Ошибка {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка создания workflow: {str(e)}"
            }
    
    def get_workflows(self) -> Dict:
        """Получение списка workflow"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows")
            
            if response.status_code == 200:
                data = response.json()
                workflows = data.get('data', [])
                return {
                    "status": "success",
                    "count": len(workflows),
                    "workflows": workflows
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Активация workflow"""
        try:
            # Получаем текущий workflow
            get_response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}")
            
            if get_response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Workflow не найден: {get_response.status_code}"
                }
            
            workflow = get_response.json()
            workflow['active'] = True
            
            # Обновляем workflow
            update_response = self.session.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                json=workflow
            )
            
            if update_response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Workflow активирован!",
                    "workflow": update_response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка активации: {update_response.status_code}",
                    "response": update_response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка активации: {str(e)}"
            }

def test_production_client():
    """Тестирование Production клиента"""
    
    # API ключ из .env
    api_key = os.getenv('N8N_API_KEY') or "your_n8n_api_key_here"
    
    client = N8NProductionClient(api_key)
    
    print("🚀 ТЕСТИРОВАНИЕ N8N PRODUCTION CLIENT")
    print("=" * 50)
    
    # 1. Получение существующих workflow
    print("\n1️⃣ Получение workflow...")
    workflows_result = client.get_workflows()
    
    if workflows_result['status'] == 'success':
        print(f"✅ Найдено {workflows_result['count']} workflow")
        for wf in workflows_result['workflows']:
            print(f"   📝 {wf.get('name', 'Unnamed')} (ID: {wf.get('id')}) {'🟢 Active' if wf.get('active') else '⚪ Inactive'}")
    else:
        print(f"❌ Ошибка: {workflows_result['message']}")
        return
    
    # 2. Создание N8N-Agent workflow
    print("\n2️⃣ Создание N8N-Agent Test Workflow...")
    
    test_workflow = {
        "name": "N8N-Agent Success Test",
        "nodes": [
            {
                "id": "webhook",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [100, 200],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "n8n-agent-test",
                    "authentication": "none"
                }
            },
            {
                "id": "set",
                "name": "Set Success",
                "type": "n8n-nodes-base.set",
                "typeVersion": 1,
                "position": [300, 200],
                "parameters": {
                    "values": {
                        "string": [
                            {"name": "status", "value": "N8N-Agent API Integration Success!"},
                            {"name": "timestamp", "value": "{{ $now }}"},
                            {"name": "workflow_created_by", "value": "N8N-Agent v1.0"}
                        ]
                    }
                }
            }
        ],
        "connections": {
            "Webhook": {
                "main": [[{
                    "node": "Set Success",
                    "type": "main",
                    "index": 0
                }]]
            }
        },
        "settings": {},
        "staticData": {}
    }
    
    create_result = client.create_workflow(test_workflow)
    
    if create_result['status'] == 'success':
        workflow_id = create_result['id']
        workflow_name = create_result['name']
        workflow_url = create_result['url']
        
        print(f"✅ Workflow создан: {workflow_name}")
        print(f"🆔 ID: {workflow_id}")
        print(f"🔗 URL: {workflow_url}")
        
        # 3. Активация workflow
        print("\n3️⃣ Активация workflow...")
        activate_result = client.activate_workflow(workflow_id)
        
        if activate_result['status'] == 'success':
            print("✅ Workflow активирован!")
            print(f"🚀 Webhook URL: http://localhost:5678/webhook/n8n-agent-test")
            print("\n🎉 N8N-AGENT ПОЛНОСТЬЮ ИНТЕГРИРОВАН С N8N!")
            
            # Сохраняем результат
            result_data = {
                "success": True,
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "workflow_url": workflow_url,
                "webhook_url": "http://localhost:5678/webhook/n8n-agent-test",
                "message": "N8N-Agent successfully integrated with n8n API!"
            }
            
            with open("/Users/hdv_1987/Desktop/Projects/N8N-Agent/INTEGRATION_SUCCESS.json", 'w') as f:
                json.dump(result_data, f, indent=2)
            
            print("💾 Результат сохранен: INTEGRATION_SUCCESS.json")
            
        else:
            print(f"❌ Ошибка активации: {activate_result['message']}")
    else:
        print(f"❌ Ошибка создания: {create_result['message']}")
        print(f"📝 Детали: {create_result.get('response', 'Нет деталей')}")

if __name__ == "__main__":
    test_production_client()
