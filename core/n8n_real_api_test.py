#!/usr/bin/env python3
"""
🧪 N8N Real API Test
Тестирование реального подключения к n8n API с JWT токеном
"""

import requests
import json
import os
from typing import Dict

class N8NRealAPITester:
    """Тестер реального n8n API"""
    
    def __init__(self):
        self.base_url = "http://localhost:5678"
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTVhZTQ3YS1hZDNmLTQ1OTYtYjE5OS05ZjA4MTE2M2M5NGQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ5MzY4Njg0LCJleHAiOjE3NTE5NDcyMDB9.bvYcgPwSgZA1GEfIuBSkQ1Kv3imRu38JGdkQnEJ18VM"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self) -> Dict:
        """Тест базового подключения"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows")
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_data": response.json() if response.status_code == 200 else response.text,
                "message": "API подключение работает!" if response.status_code == 200 else f"Ошибка: {response.status_code}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка подключения: {str(e)}"
            }
    
    def get_workflows(self) -> Dict:
        """Получение списка workflow"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows")
            
            if response.status_code == 200:
                workflows = response.json()
                return {
                    "status": "success",
                    "count": len(workflows.get('data', [])),
                    "workflows": workflows.get('data', [])
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
    
    def create_test_workflow(self) -> Dict:
        """Создание тестового workflow"""
        
        test_workflow = {
            "name": "N8N-Agent Test Workflow",
            "active": False,
            "nodes": [
                {
                    "id": "1",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "typeVersion": 1,
                    "position": [100, 200],
                    "parameters": {}
                },
                {
                    "id": "2",
                    "name": "Set",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 1,
                    "position": [300, 200],
                    "parameters": {
                        "values": {
                            "string": [
                                {"name": "message", "value": "N8N-Agent API Test Successful!"},
                                {"name": "timestamp", "value": "{{ $now }}"}
                            ]
                        }
                    }
                }
            ],
            "connections": {
                "Start": {
                    "main": [[{
                        "node": "Set",
                        "type": "main",
                        "index": 0
                    }]]
                }
            },
            "settings": {},
            "staticData": {}
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows",
                json=test_workflow
            )
            
            if response.status_code in [200, 201]:
                created_workflow = response.json()
                return {
                    "status": "success",
                    "workflow": created_workflow,
                    "message": "Тестовый workflow создан успешно!"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка создания: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Активация workflow"""
        try:
            # Сначала получаем workflow
            get_response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}")
            
            if get_response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Workflow не найден: {get_response.status_code}"
                }
            
            workflow_data = get_response.json()
            workflow_data['active'] = True
            
            # Обновляем workflow с активацией
            response = self.session.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                json=workflow_data
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Workflow активирован!",
                    "workflow": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка активации: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }
    
    def run_full_test(self) -> None:
        """Полное тестирование API"""
        
        print("🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ N8N REAL API")
        print("=" * 50)
        
        # 1. Тест подключения
        print("\n1️⃣ Тестирование подключения...")
        connection_result = self.test_connection()
        
        if connection_result['status'] == 'success':
            print("✅ Подключение успешно!")
            print(f"📊 Статус: {connection_result['status_code']}")
        else:
            print(f"❌ Ошибка подключения: {connection_result['message']}")
            return
        
        # 2. Получение существующих workflow
        print("\n2️⃣ Получение списка workflow...")
        workflows_result = self.get_workflows()
        
        if workflows_result['status'] == 'success':
            print(f"✅ Получено {workflows_result['count']} workflow")
            for wf in workflows_result['workflows'][:3]:  # Показываем первые 3
                print(f"   📝 {wf.get('name', 'Unnamed')} (ID: {wf.get('id')})")
        else:
            print(f"❌ Ошибка получения workflow: {workflows_result['message']}")
        
        # 3. Создание тестового workflow
        print("\n3️⃣ Создание тестового workflow...")
        create_result = self.create_test_workflow()
        
        if create_result['status'] == 'success':
            workflow_id = create_result['workflow']['id']
            workflow_name = create_result['workflow']['name']
            print(f"✅ Workflow создан: {workflow_name}")
            print(f"🆔 ID: {workflow_id}")
            
            # 4. Активация workflow
            print("\n4️⃣ Активация workflow...")
            activate_result = self.activate_workflow(workflow_id)
            
            if activate_result['status'] == 'success':
                print("✅ Workflow активирован!")
                print(f"🔗 URL: http://localhost:5678/workflow/{workflow_id}")
            else:
                print(f"❌ Ошибка активации: {activate_result['message']}")
                
        else:
            print(f"❌ Ошибка создания workflow: {create_result['message']}")
        
        print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 50)

def main():
    tester = N8NRealAPITester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
