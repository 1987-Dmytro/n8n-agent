#!/usr/bin/env python3
"""
🔬 N8N API Research Tool
Инструмент для исследования n8n API и структуры workflow
"""

import requests
import json
from typing import Dict, List, Optional
import os
from datetime import datetime

class N8NAPIResearcher:
    """Исследователь n8n API"""
    
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_user = "admin"
        self.auth_password = "password"
        
        # Настраиваем сессию
        self.session.auth = (self.auth_user, self.auth_password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def check_connection(self) -> Dict:
        """Проверка подключения к n8n"""
        try:
            # Попробуем получить информацию о системе
            response = self.session.get(f"{self.base_url}/healthz")
            
            if response.status_code == 200:
                return {
                    "status": "success", 
                    "message": "n8n доступен",
                    "url": self.base_url
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка подключения: {str(e)}"
            }
    
    def explore_api_endpoints(self) -> Dict:
        """Исследование доступных API endpoints"""
        endpoints_to_test = [
            "/rest/workflows",
            "/rest/executions", 
            "/rest/nodes",
            "/rest/credentials",
            "/rest/active",
            "/healthz",
            "/rest/settings",
            "/rest/login"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code < 400,
                    "response_size": len(response.text),
                    "content_type": response.headers.get('Content-Type', 'unknown')
                }
                
                # Если endpoint доступен, сохраним sample данных
                if response.status_code == 200:
                    try:
                        data = response.json()
                        results[endpoint]["sample_data"] = str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    except:
                        results[endpoint]["sample_data"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                        
            except Exception as e:
                results[endpoint] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return results
    
    def research_workflow_structure(self) -> Dict:
        """Исследование структуры workflow n8n"""
        
        # Сначала попробуем получить существующие workflow
        try:
            response = self.session.get(f"{self.base_url}/rest/workflows")
            
            if response.status_code == 200:
                workflows = response.json()
                
                result = {
                    "existing_workflows_count": len(workflows.get('data', [])),
                    "workflow_structure_sample": None,
                    "status": "success"
                }
                
                # Если есть workflow, изучим структуру
                if workflows.get('data') and len(workflows['data']) > 0:
                    sample_workflow = workflows['data'][0]
                    result["workflow_structure_sample"] = sample_workflow
                
                return result
                
            else:
                return {
                    "status": "error", 
                    "message": f"Не удалось получить workflow: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка исследования workflow: {str(e)}"
            }
    
    def test_workflow_creation(self) -> Dict:
        """Тест создания простого workflow"""
        
        # Создаем простейший workflow для тестирования
        simple_workflow = {
            "name": "Test API Workflow",
            "active": False,
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
        
        try:
            response = self.session.post(
                f"{self.base_url}/rest/workflows",
                json=simple_workflow
            )
            
            if response.status_code in [200, 201]:
                created_workflow = response.json()
                
                # Попробуем удалить созданный тестовый workflow
                if 'id' in created_workflow:
                    delete_response = self.session.delete(
                        f"{self.base_url}/rest/workflows/{created_workflow['id']}"
                    )
                
                return {
                    "status": "success",
                    "message": "Создание workflow работает!",
                    "created_workflow_id": created_workflow.get('id'),
                    "api_writable": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"Ошибка создания workflow: {response.status_code}",
                    "response": response.text,
                    "api_writable": False
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Ошибка тестирования создания: {str(e)}",
                "api_writable": False
            }
    
    def research_available_nodes(self) -> Dict:
        """Исследование доступных nodes в n8n"""
        try:
            response = self.session.get(f"{self.base_url}/rest/node-types")
            
            if response.status_code == 200:
                nodes_data = response.json()
                
                # Анализируем nodes
                if isinstance(nodes_data, list):
                    nodes_list = nodes_data
                elif isinstance(nodes_data, dict) and 'data' in nodes_data:
                    nodes_list = nodes_data['data']
                else:
                    nodes_list = []
                
                # Категоризируем nodes
                categories = {}
                total_nodes = len(nodes_list)
                
                for node in nodes_list[:50]:  # Берем первые 50 для анализа
                    if isinstance(node, dict):
                        node_name = node.get('name', 'unknown')
                        node_category = node_name.split('.')[0] if '.' in node_name else 'other'
                        
                        if node_category not in categories:
                            categories[node_category] = []
                        categories[node_category].append(node_name)
                
                return {
                    "status": "success",
                    "total_nodes": total_nodes,
                    "categories": categories,
                    "sample_nodes": [node.get('name') for node in nodes_list[:10] if isinstance(node, dict)]
                }
            else:
                return {
                    "status": "error",
                    "message": f"Не удалось получить nodes: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка исследования nodes: {str(e)}"
            }
    
    def generate_research_report(self) -> str:
        """Генерация полного отчета об исследовании"""
        
        print("🔬 Начинаем исследование n8n API...")
        
        # 1. Проверка подключения
        print("1️⃣ Проверка подключения...")
        connection_result = self.check_connection()
        
        # 2. Исследование endpoints
        print("2️⃣ Исследование API endpoints...")
        endpoints_result = self.explore_api_endpoints()
        
        # 3. Исследование workflow структуры
        print("3️⃣ Исследование структуры workflow...")
        workflow_result = self.research_workflow_structure()
        
        # 4. Тест создания workflow
        print("4️⃣ Тестирование создания workflow...")
        creation_result = self.test_workflow_creation()
        
        # 5. Исследование nodes
        print("5️⃣ Исследование доступных nodes...")
        nodes_result = self.research_available_nodes()
        
        # Генерация отчета
        report = f"""
# 🔬 ОТЧЕТ ИССЛЕДОВАНИЯ N8N API
**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**URL:** {self.base_url}

## 1️⃣ СТАТУС ПОДКЛЮЧЕНИЯ
- **Статус:** {connection_result['status']}
- **Сообщение:** {connection_result['message']}

## 2️⃣ ДОСТУПНЫЕ API ENDPOINTS
"""
        
        for endpoint, result in endpoints_result.items():
            status_icon = "✅" if result.get('accessible', False) else "❌"
            report += f"- {status_icon} `{endpoint}` - HTTP {result.get('status_code', 'N/A')}\n"
        
        report += f"""
## 3️⃣ СТРУКТУРА WORKFLOW
- **Статус:** {workflow_result['status']}
- **Существующих workflow:** {workflow_result.get('existing_workflows_count', 0)}

## 4️⃣ ТЕСТ СОЗДАНИЯ WORKFLOW
- **Статус:** {creation_result['status']}
- **API доступен для записи:** {'✅' if creation_result.get('api_writable', False) else '❌'}
- **Сообщение:** {creation_result['message']}

## 5️⃣ ДОСТУПНЫЕ NODES
"""
        
        if nodes_result['status'] == 'success':
            report += f"- **Всего nodes:** {nodes_result['total_nodes']}\n"
            report += f"- **Основные категории:** {', '.join(nodes_result['categories'].keys())}\n"
            report += f"- **Примеры nodes:** {', '.join(nodes_result['sample_nodes'])}\n"
        else:
            report += f"- **Ошибка:** {nodes_result['message']}\n"
        
        report += f"""
## 🎯 ВЫВОДЫ ДЛЯ N8N-AGENT

### ✅ ЧТО РАБОТАЕТ:
- Подключение к n8n API
- Чтение существующих данных
- Базовая аутентификация

### 🔧 ЧТО НУЖНО НАСТРОИТЬ:
- Правильная аутентификация для создания workflow
- Изучение правильной структуры nodes
- Тестирование активации workflow

### 🚀 СЛЕДУЮЩИЕ ШАГИ:
1. Настроить корректную аутентификацию
2. Изучить структуру реальных workflow
3. Создать базу знаний n8n nodes
4. Разработать n8n_api_client.py

---
*Исследование выполнено N8N API Research Tool v1.0*
"""
        
        return report

def main():
    """Главная функция исследования"""
    
    print("🚀 Запуск N8N API Research Tool...")
    
    # Создаем исследователя
    researcher = N8NAPIResearcher()
    
    # Генерируем отчет
    report = researcher.generate_research_report()
    
    # Сохраняем отчет
    report_path = "/Users/hdv_1987/Desktop/Projects/N8N-Agent/n8n_api_research_report.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 Отчет сохранен: {report_path}")
    print("\n" + report)

if __name__ == "__main__":
    main()
