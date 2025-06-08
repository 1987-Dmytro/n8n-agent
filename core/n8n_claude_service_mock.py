#!/usr/bin/env python3
"""
🧪 N8N Claude Service Mock
Mock версия для тестирования без Claude API
"""

import json
from n8n_knowledge_base import N8NKnowledgeBase

class N8NClaudeServiceMock:
    """Mock версия Claude Service для тестирования"""
    
    def __init__(self):
        self.knowledge_base = N8NKnowledgeBase()
    
    def generate_workflow(self, description: str, params: dict = None) -> dict:
        """Mock генерация workflow"""
        
        if params is None:
            params = {}
        
        # Простая логика создания workflow на основе описания
        workflow = self._create_mock_workflow(description, params)
        
        return {
            "status": "success",
            "workflow": workflow,
            "description": description,
            "params": params,
            "claude_response": "Mock response - workflow generated successfully"
        }
    
    def _create_mock_workflow(self, description: str, params: dict) -> dict:
        """Создание mock workflow на основе паттернов"""
        
        description_lower = description.lower()
        
        # Определяем тип workflow
        if any(word in description_lower for word in ['webhook', 'получать']) and any(word in description_lower for word in ['slack', 'уведомление']):
            return self._create_webhook_to_slack_workflow(description)
        
        elif any(word in description_lower for word in ['каждый', 'час']) and any(word in description_lower for word in ['api', 'sheets']):
            return self._create_scheduled_api_to_sheets_workflow(description)
        
        else:
            return self._create_simple_webhook_workflow(description)
    
    def _create_webhook_to_slack_workflow(self, description: str) -> dict:
        """Webhook → Slack workflow"""
        return {
            "name": "Webhook to Slack Notification",
            "nodes": [
                {
                    "id": "1",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "notification",
                        "authentication": "none"
                    }
                },
                {
                    "id": "2", 
                    "name": "Set Data",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 1,
                    "position": [300, 200],
                    "parameters": {
                        "values": {
                            "string": [
                                {"name": "processed_at", "value": "{{ $now }}"},
                                {"name": "status", "value": "received"}
                            ]
                        }
                    }
                },
                {
                    "id": "3",
                    "name": "Slack",
                    "type": "n8n-nodes-base.slack", 
                    "typeVersion": 1,
                    "position": [500, 200],
                    "parameters": {
                        "operation": "postMessage",
                        "channel": "#notifications",
                        "text": "Получен webhook: {{ $json.data }}"
                    }
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{
                        "node": "Set Data",
                        "type": "main",
                        "index": 0
                    }]]
                },
                "Set Data": {
                    "main": [[{
                        "node": "Slack",
                        "type": "main", 
                        "index": 0
                    }]]
                }
            },
            "settings": {},
            "staticData": {}
        }
    
    def _create_scheduled_api_to_sheets_workflow(self, description: str) -> dict:
        """Schedule → API → Google Sheets workflow"""
        return {
            "name": "Scheduled API to Google Sheets",
            "nodes": [
                {
                    "id": "1",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.schedule",
                    "typeVersion": 1,
                    "position": [100, 200],
                    "parameters": {
                        "rule": "interval",
                        "interval": 60
                    }
                },
                {
                    "id": "2",
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [300, 200],
                    "parameters": {
                        "url": "https://api.example.com/data",
                        "method": "GET",
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    }
                },
                {
                    "id": "3",
                    "name": "Google Sheets",
                    "type": "n8n-nodes-base.googleSheets",
                    "typeVersion": 1,
                    "position": [500, 200],
                    "parameters": {
                        "operation": "append",
                        "sheetId": "your_sheet_id",
                        "range": "A:C",
                        "values": [
                            ["{{ $json.timestamp }}", "{{ $json.value }}", "{{ $json.status }}"]
                        ]
                    }
                }
            ],
            "connections": {
                "Schedule Trigger": {
                    "main": [[{
                        "node": "HTTP Request",
                        "type": "main",
                        "index": 0
                    }]]
                },
                "HTTP Request": {
                    "main": [[{
                        "node": "Google Sheets",
                        "type": "main",
                        "index": 0
                    }]]
                }
            },
            "settings": {},
            "staticData": {}
        }
    
    def _create_simple_webhook_workflow(self, description: str) -> dict:
        """Простой webhook workflow"""
        return {
            "name": "Simple Webhook Workflow",
            "nodes": [
                {
                    "id": "1",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "simple",
                        "authentication": "none"
                    }
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
                                {"name": "result", "value": "processed"},
                                {"name": "timestamp", "value": "{{ $now }}"}
                            ]
                        }
                    }
                }
            ],
            "connections": {
                "Webhook": {
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

def test_mock_service():
    """Тестирование Mock сервиса"""
    
    print("🧪 Тестирование N8N Claude Service Mock...")
    
    service = N8NClaudeServiceMock()
    
    test_cases = [
        "При получении webhook отправить уведомление в Slack",
        "Каждый час получать данные из API и сохранять в Google Sheets", 
        "Простая обработка webhook данных"
    ]
    
    for i, description in enumerate(test_cases):
        print(f"\n📝 Тест {i+1}: {description}")
        
        result = service.generate_workflow(description)
        
        if result['status'] == 'success':
            workflow = result['workflow']
            print(f"✅ Workflow создан: {workflow['name']}")
            print(f"🔧 Nodes: {len(workflow['nodes'])}")
            print(f"🔗 Connections: {len(workflow['connections'])}")
            
            # Сохраняем результат
            output_path = f"/Users/hdv_1987/Desktop/Projects/N8N-Agent/examples/mock_workflow_{i+1}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"💾 Сохранен: {output_path}")
        else:
            print(f"❌ Ошибка: {result['message']}")
    
    print(f"\n🎉 Mock тестирование завершено!")

if __name__ == "__main__":
    test_mock_service()
