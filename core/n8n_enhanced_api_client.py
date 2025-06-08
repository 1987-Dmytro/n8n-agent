#!/usr/bin/env python3
"""
🔧 N8N Enhanced API Client
Клиент для работы с n8n API с поддержкой разных методов аутентификации
"""

import requests
import json
from typing import Dict, List, Optional, Any
import os
from datetime import datetime
import urllib.parse

class N8NAPIClient:
    """Улучшенный клиент для работы с n8n API"""
    
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"  # Public API endpoint
        self.rest_base = f"{self.base_url}/rest"   # Internal REST endpoint
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'N8N-Agent/1.0'
        })
        
        self.authenticated = False
        self.auth_method = None
        
    def authenticate_with_email(self, email: str, password: str) -> Dict:
        """Аутентификация через email/password"""
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            response = self.session.post(
                f"{self.rest_base}/login",
                json=login_data
            )
            
            if response.status_code == 200:
                self.authenticated = True
                self.auth_method = "session"
                return {
                    "status": "success",
                    "message": "Аутентификация успешна",
                    "method": "email/password"
                }
            else:
                return {
                    "status": "error", 
                    "message": f"Ошибка аутентификации: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка аутентификации: {str(e)}"
            }
    
    def authenticate_with_api_key(self, api_key: str) -> Dict:
        """Аутентификация через API ключ"""
        try:
            self.session.headers.update({
                'X-N8N-API-KEY': api_key
            })
            
            # Тестируем доступ
            response = self.session.get(f"{self.api_base}/workflows")
            
            if response.status_code == 200:
                self.authenticated = True
                self.auth_method = "api_key"
                return {
                    "status": "success",
                    "message": "API ключ работает",
                    "method": "api_key"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Неверный API ключ: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка API ключа: {str(e)}"
            }
    
    def check_authentication(self) -> Dict:
        """Проверка статуса аутентификации"""
        if not self.authenticated:
            return {"authenticated": False, "message": "Не аутентифицирован"}
        
        try:
            # Проверяем доступ к API
            if self.auth_method == "api_key":
                response = self.session.get(f"{self.api_base}/workflows")
            else:
                response = self.session.get(f"{self.rest_base}/workflows")
            
            if response.status_code == 200:
                return {
                    "authenticated": True,
                    "method": self.auth_method,
                    "status": "active"
                }
            else:
                return {
                    "authenticated": False,
                    "message": f"Аутентификация потеряна: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "authenticated": False,
                "message": f"Ошибка проверки: {str(e)}"
            }
    
    def get_workflows(self) -> Dict:
        """Получение списка workflow"""
        if not self.authenticated:
            return {"status": "error", "message": "Не аутентифицирован"}
        
        try:
            endpoint = f"{self.api_base}/workflows" if self.auth_method == "api_key" else f"{self.rest_base}/workflows"
            response = self.session.get(endpoint)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "workflows": response.json(),
                    "count": len(response.json().get('data', []))
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка получения workflow: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }
    
    def create_workflow(self, workflow_data: Dict) -> Dict:
        """Создание workflow"""
        if not self.authenticated:
            return {"status": "error", "message": "Не аутентифицирован"}
        
        try:
            endpoint = f"{self.api_base}/workflows" if self.auth_method == "api_key" else f"{self.rest_base}/workflows"
            
            response = self.session.post(endpoint, json=workflow_data)
            
            if response.status_code in [200, 201]:
                created_workflow = response.json()
                return {
                    "status": "success",
                    "workflow": created_workflow,
                    "id": created_workflow.get('id'),
                    "message": "Workflow создан успешно"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка создания workflow: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Ошибка создания workflow: {str(e)}"
            }
    
    def activate_workflow(self, workflow_id: str) -> Dict:
        """Активация workflow"""
        if not self.authenticated:
            return {"status": "error", "message": "Не аутентифицирован"}
        
        try:
            endpoint = f"{self.api_base}/workflows/{workflow_id}/activate" if self.auth_method == "api_key" else f"{self.rest_base}/workflows/{workflow_id}/activate"
            
            response = self.session.post(endpoint)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Workflow активирован",
                    "workflow_id": workflow_id
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
                "message": f"Ошибка активации: {str(e)}"
            }
    
    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """Выполнение workflow"""
        if not self.authenticated:
            return {"status": "error", "message": "Не аутентифицирован"}
        
        try:
            endpoint = f"{self.api_base}/workflows/{workflow_id}/execute" if self.auth_method == "api_key" else f"{self.rest_base}/workflows/{workflow_id}/execute"
            
            payload = {"data": data} if data else {}
            response = self.session.post(endpoint, json=payload)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "execution": response.json(),
                    "message": "Workflow выполнен"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка выполнения: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка выполнения: {str(e)}"
            }
    
    def get_node_types(self) -> Dict:
        """Получение доступных типов nodes"""
        try:
            # Этот endpoint обычно доступен без аутентификации
            response = self.session.get(f"{self.rest_base}/node-types")
            
            if response.status_code == 200:
                node_types = response.json()
                return {
                    "status": "success",
                    "node_types": node_types,
                    "count": len(node_types) if isinstance(node_types, list) else len(node_types.get('data', []))
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка получения nodes: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }
    
    def test_connection(self) -> Dict:
        """Полное тестирование подключения и возможностей"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "tests": {}
        }
        
        # 1. Тест базового подключения
        try:
            response = self.session.get(f"{self.base_url}/healthz")
            results["tests"]["basic_connection"] = {
                "status": "success" if response.status_code == 200 else "error",
                "code": response.status_code
            }
        except Exception as e:
            results["tests"]["basic_connection"] = {
                "status": "error",
                "message": str(e)
            }
        
        # 2. Тест аутентификации
        auth_check = self.check_authentication()
        results["tests"]["authentication"] = auth_check
        
        # 3. Тест доступа к workflow
        if self.authenticated:
            workflows_result = self.get_workflows()
            results["tests"]["workflows_access"] = workflows_result
        
        # 4. Тест получения node types
        nodes_result = self.get_node_types()
        results["tests"]["node_types_access"] = nodes_result
        
        return results


def test_n8n_api():
    """Тестирование N8N API Client"""
    
    print("🧪 Тестирование N8N Enhanced API Client...")
    
    # Создаем клиент
    client = N8NAPIClient()
    
    # Полное тестирование
    test_results = client.test_connection()
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"🕐 Время: {test_results['timestamp']}")
    print(f"🔗 URL: {test_results['base_url']}")
    
    for test_name, result in test_results['tests'].items():
        status_icon = "✅" if result.get('status') == 'success' else "❌"
        print(f"{status_icon} {test_name}: {result.get('status', 'unknown')}")
        if result.get('message'):
            print(f"   📝 {result['message']}")
    
    # Сохраняем результаты
    report_path = "/Users/hdv_1987/Desktop/Projects/N8N-Agent/n8n_api_test_results.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены: {report_path}")
    
    return test_results

if __name__ == "__main__":
    test_n8n_api()
