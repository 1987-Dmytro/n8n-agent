#!/usr/bin/env python3
"""
📚 N8N Knowledge Base
База знаний n8n nodes для генерации workflow
"""

from typing import Dict, List, Optional, Any
import yaml
import json

class N8NKnowledgeBase:
    """База знаний n8n nodes и их возможностей"""
    
    def __init__(self):
        self.nodes = self._initialize_nodes()
        self.categories = self._categorize_nodes()
        self.workflow_patterns = self._initialize_patterns()
    
    def _initialize_nodes(self) -> Dict[str, Dict]:
        """Инициализация базы знаний nodes"""
        return {
            # === TRIGGER NODES ===
            "n8n-nodes-base.webhook": {
                "category": "trigger",
                "display_name": "Webhook",
                "description": "Получение HTTP запросов для запуска workflow",
                "parameters": {
                    "httpMethod": {"type": "options", "options": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                    "path": {"type": "string", "description": "URL path для webhook"},
                    "authentication": {"type": "options", "options": ["none", "basicAuth", "headerAuth"]}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Получение данных от внешних систем",
                    "Интеграция с третьими сторонами",
                    "Автоматический запуск при событиях"
                ],
                "example_config": {
                    "httpMethod": "POST",
                    "path": "webhook-data",
                    "authentication": "none"
                }
            },
            
            "n8n-nodes-base.schedule": {
                "category": "trigger", 
                "display_name": "Schedule Trigger",
                "description": "Запуск workflow по расписанию",
                "parameters": {
                    "rule": {"type": "options", "options": ["interval", "cron"]},
                    "interval": {"type": "number", "description": "Интервал в минутах"},
                    "cronExpression": {"type": "string", "description": "Cron выражение"}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Регулярная обработка данных",
                    "Периодические отчеты",
                    "Автоматическая синхронизация"
                ]
            },
            
            # === HTTP NODES ===
            "n8n-nodes-base.httpRequest": {
                "category": "regular",
                "display_name": "HTTP Request",
                "description": "Выполнение HTTP запросов к API",
                "parameters": {
                    "url": {"type": "string", "required": True},
                    "method": {"type": "options", "options": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                    "headers": {"type": "fixedCollection", "description": "HTTP заголовки"},
                    "body": {"type": "json", "description": "Тело запроса"},
                    "authentication": {"type": "options", "options": ["none", "basicAuth", "oAuth2", "apiKey"]}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Интеграция с REST API",
                    "Получение данных от сервисов",
                    "Отправка данных в системы"
                ],
                "example_config": {
                    "url": "https://api.example.com/data",
                    "method": "GET",
                    "headers": {"Content-Type": "application/json"}
                }
            },
            
            # === GOOGLE SERVICES ===
            "n8n-nodes-base.googleSheets": {
                "category": "regular",
                "display_name": "Google Sheets",
                "description": "Работа с Google Таблицами",
                "parameters": {
                    "operation": {"type": "options", "options": ["append", "read", "update", "clear"]},
                    "sheetId": {"type": "string", "required": True},
                    "range": {"type": "string", "description": "Диапазон ячеек (A1:C10)"},
                    "values": {"type": "array", "description": "Данные для записи"}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Сохранение данных в таблицы",
                    "Чтение конфигураций",
                    "Создание отчетов"
                ],
                "connection_required": "googleSheetsOAuth2Api"
            },
            
            "n8n-nodes-base.gmail": {
                "category": "regular",
                "display_name": "Gmail",
                "description": "Отправка и получение email через Gmail",
                "parameters": {
                    "operation": {"type": "options", "options": ["send", "get", "getAll"]},
                    "to": {"type": "string", "description": "Email получателя"},
                    "subject": {"type": "string", "description": "Тема письма"},
                    "message": {"type": "string", "description": "Текст сообщения"},
                    "attachments": {"type": "fixedCollection", "description": "Вложения"}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Отправка уведомлений",
                    "Автоматические отчеты",
                    "Обработка входящей почты"
                ],
                "connection_required": "gmailOAuth2"
            },
            
            # === COMMUNICATION ===
            "n8n-nodes-base.slack": {
                "category": "regular",
                "display_name": "Slack",
                "description": "Интеграция со Slack",
                "parameters": {
                    "operation": {"type": "options", "options": ["postMessage", "update", "get"]},
                    "channel": {"type": "string", "description": "Канал Slack"},
                    "text": {"type": "string", "description": "Текст сообщения"},
                    "username": {"type": "string", "description": "Имя бота"},
                    "attachments": {"type": "fixedCollection", "description": "Вложения"}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Уведомления команды",
                    "Алерты системы",
                    "Интерактивные боты"
                ],
                "connection_required": "slackApi"
            },
            
            # === DATA PROCESSING ===
            "n8n-nodes-base.set": {
                "category": "regular",
                "display_name": "Set",
                "description": "Установка и модификация данных",
                "parameters": {
                    "values": {"type": "fixedCollection", "description": "Поля для установки"},
                    "options": {"type": "collection", "description": "Дополнительные опции"}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Трансформация данных",
                    "Добавление полей",
                    "Изменение структуры"
                ],
                "example_config": {
                    "values": {
                        "string": [
                            {"name": "processed_at", "value": "{{ $now }}"},
                            {"name": "status", "value": "completed"}
                        ]
                    }
                }
            },
            
            "n8n-nodes-base.if": {
                "category": "regular",
                "display_name": "IF",
                "description": "Условная логика",
                "parameters": {
                    "conditions": {"type": "fixedCollection", "description": "Условия для проверки"},
                    "combineOperation": {"type": "options", "options": ["any", "all"]}
                },
                "outputs": ["main", "fallback"],
                "use_cases": [
                    "Условная обработка",
                    "Фильтрация данных", 
                    "Ветвление логики"
                ]
            },
            
            "n8n-nodes-base.switch": {
                "category": "regular",
                "display_name": "Switch",
                "description": "Множественное ветвление",
                "parameters": {
                    "mode": {"type": "options", "options": ["expression", "rules"]},
                    "value": {"type": "string", "description": "Значение для сравнения"},
                    "rules": {"type": "fixedCollection", "description": "Правила ветвления"}
                },
                "outputs": ["main", "fallback"],
                "use_cases": [
                    "Маршрутизация данных",
                    "Множественные условия",
                    "Обработка разных типов"
                ]
            },
            
            # === UTILITIES ===
            "n8n-nodes-base.merge": {
                "category": "regular",
                "display_name": "Merge",
                "description": "Объединение данных из разных источников",
                "parameters": {
                    "mode": {"type": "options", "options": ["append", "merge", "multiplex"]},
                    "joinMode": {"type": "options", "options": ["inner", "left", "outer"]}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Объединение данных",
                    "Синхронизация потоков",
                    "Агрегация результатов"
                ]
            },
            
            "n8n-nodes-base.wait": {
                "category": "regular", 
                "display_name": "Wait",
                "description": "Пауза в выполнении workflow",
                "parameters": {
                    "amount": {"type": "number", "description": "Время ожидания"},
                    "unit": {"type": "options", "options": ["seconds", "minutes", "hours", "days"]}
                },
                "outputs": ["main"],
                "use_cases": [
                    "Задержка обработки",
                    "Ожидание внешних событий",
                    "Throttling запросов"
                ]
            }
        }
    
    def _categorize_nodes(self) -> Dict[str, List[str]]:
        """Категоризация nodes"""
        categories = {}
        
        for node_name, node_info in self.nodes.items():
            category = node_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(node_name)
        
        return categories
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Инициализация паттернов workflow"""
        return {
            "webhook_to_action": {
                "description": "Получение webhook и выполнение действия",
                "nodes": ["n8n-nodes-base.webhook", "n8n-nodes-base.set"],
                "connections": [{"from": 0, "to": 1}],
                "use_case": "Простая обработка входящих данных"
            },
            
            "scheduled_data_sync": {
                "description": "Периодическая синхронизация данных",
                "nodes": ["n8n-nodes-base.schedule", "n8n-nodes-base.httpRequest", "n8n-nodes-base.googleSheets"],
                "connections": [{"from": 0, "to": 1}, {"from": 1, "to": 2}],
                "use_case": "Регулярное получение и сохранение данных"
            },
            
            "conditional_notification": {
                "description": "Условные уведомления",
                "nodes": ["n8n-nodes-base.webhook", "n8n-nodes-base.if", "n8n-nodes-base.slack", "n8n-nodes-base.gmail"],
                "connections": [
                    {"from": 0, "to": 1},
                    {"from": 1, "to": 2, "output": "main"},
                    {"from": 1, "to": 3, "output": "fallback"}
                ],
                "use_case": "Разные уведомления в зависимости от условий"
            },
            
            "api_to_multiple_destinations": {
                "description": "Получение данных и отправка в несколько мест",
                "nodes": ["n8n-nodes-base.httpRequest", "n8n-nodes-base.set", "n8n-nodes-base.googleSheets", "n8n-nodes-base.slack"],
                "connections": [
                    {"from": 0, "to": 1},
                    {"from": 1, "to": 2},
                    {"from": 1, "to": 3}
                ],
                "use_case": "Распределение данных по системам"
            }
        }
    
    def get_node_info(self, node_name: str) -> Optional[Dict]:
        """Получение информации о node"""
        return self.nodes.get(node_name)
    
    def get_nodes_by_category(self, category: str) -> List[str]:
        """Получение nodes по категории"""
        return self.categories.get(category, [])
    
    def find_nodes_by_use_case(self, use_case_keywords: List[str]) -> List[str]:
        """Поиск nodes по ключевым словам use case"""
        matching_nodes = []
        
        for node_name, node_info in self.nodes.items():
            use_cases = node_info.get('use_cases', [])
            use_cases_text = ' '.join(use_cases).lower()
            
            if any(keyword.lower() in use_cases_text for keyword in use_case_keywords):
                matching_nodes.append(node_name)
        
        return matching_nodes
    
    def suggest_workflow_pattern(self, description: str) -> Optional[Dict]:
        """Предложение паттерна workflow на основе описания"""
        description_lower = description.lower()
        
        # Простая эвристика для выбора паттерна
        if any(word in description_lower for word in ['webhook', 'получать', 'принимать']):
            if any(word in description_lower for word in ['если', 'условие', 'когда']):
                return self.workflow_patterns.get('conditional_notification')
            else:
                return self.workflow_patterns.get('webhook_to_action')
        
        elif any(word in description_lower for word in ['каждый', 'периодически', 'регулярно', 'час']):
            return self.workflow_patterns.get('scheduled_data_sync')
        
        elif any(word in description_lower for word in ['api', 'данные']) and any(word in description_lower for word in ['несколько', 'разные']):
            return self.workflow_patterns.get('api_to_multiple_destinations')
        
        return None
    
    def generate_node_config(self, node_name: str, custom_params: Dict = None) -> Dict:
        """Генерация конфигурации node"""
        node_info = self.get_node_info(node_name)
        if not node_info:
            return {}
        
        config = {
            "id": "temp_id",
            "name": node_info['display_name'],
            "type": node_name,
            "typeVersion": 1,
            "position": [0, 0],
            "parameters": {}
        }
        
        # Добавляем example_config если есть
        if 'example_config' in node_info:
            config['parameters'].update(node_info['example_config'])
        
        # Переопределяем custom параметрами
        if custom_params:
            config['parameters'].update(custom_params)
        
        return config
    
    def export_to_yaml(self, file_path: str):
        """Экспорт базы знаний в YAML"""
        export_data = {
            "nodes": self.nodes,
            "categories": self.categories,
            "workflow_patterns": self.workflow_patterns
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)

# Пример использования
if __name__ == "__main__":
    # Создаем базу знаний
    kb = N8NKnowledgeBase()
    
    print("📚 N8N Knowledge Base инициализирована!")
    print(f"🔧 Nodes: {len(kb.nodes)}")
    print(f"📂 Категории: {list(kb.categories.keys())}")
    print(f"🎯 Паттерны: {len(kb.workflow_patterns)}")
    
    # Экспортируем в YAML
    yaml_path = "/Users/hdv_1987/Desktop/Projects/N8N-Agent/config/n8n_nodes.yaml"
    kb.export_to_yaml(yaml_path)
    print(f"💾 База знаний экспортирована: {yaml_path}")
    
    # Примеры использования
    print("\n🔍 ПРИМЕРЫ ПОИСКА:")
    
    # Поиск по категории
    trigger_nodes = kb.get_nodes_by_category('trigger')
    print(f"Trigger nodes: {[kb.nodes[n]['display_name'] for n in trigger_nodes]}")
    
    # Поиск по use case
    email_nodes = kb.find_nodes_by_use_case(['email', 'уведомления'])
    print(f"Email nodes: {[kb.nodes[n]['display_name'] for n in email_nodes]}")
    
    # Предложение паттерна
    pattern = kb.suggest_workflow_pattern("При получении webhook отправить уведомление в Slack")
    if pattern:
        print(f"Предложенный паттерн: {pattern['description']}")
