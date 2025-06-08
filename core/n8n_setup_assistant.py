#!/usr/bin/env python3
"""
🛠️ N8N Setup Assistant
Помощник для быстрой настройки n8n и получения API доступа
"""

import requests
import json
import time
from typing import Dict, Optional
import webbrowser

class N8NSetupAssistant:
    """Помощник для настройки n8n"""
    
    def __init__(self, base_url: str = "http://localhost:5678"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def check_n8n_status(self) -> Dict:
        """Проверка статуса n8n"""
        try:
            # Проверяем health endpoint
            health_response = self.session.get(f"{self.base_url}/healthz")
            
            if health_response.status_code == 200:
                # Проверяем доступность веб-интерфейса
                web_response = self.session.get(self.base_url)
                
                return {
                    "status": "success",
                    "health": "ok",
                    "web_accessible": web_response.status_code == 200,
                    "url": self.base_url,
                    "ready_for_setup": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"n8n недоступен: {health_response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка подключения: {str(e)}"
            }
    
    def open_n8n_in_browser(self) -> Dict:
        """Открытие n8n в браузере"""
        try:
            print(f"🌐 Открываем n8n в браузере: {self.base_url}")
            webbrowser.open(self.base_url)
            
            return {
                "status": "success",
                "message": "n8n открыт в браузере",
                "url": self.base_url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Не удалось открыть браузер: {str(e)}"
            }
    
    def check_if_user_exists(self) -> Dict:
        """Проверка существования пользователей"""
        try:
            # Попробуем получить информацию о настройках
            response = self.session.get(f"{self.base_url}/rest/settings")
            
            if response.status_code == 200:
                settings = response.json()
                data = settings.get('data', {})
                
                # Проверяем настройки user management
                user_mgmt = data.get('userManagement', {})
                show_setup = user_mgmt.get('showSetupOnFirstLoad', True)
                
                return {
                    "status": "success",
                    "needs_setup": show_setup,
                    "user_management_enabled": bool(user_mgmt),
                    "settings": user_mgmt
                }
            else:
                return {
                    "status": "error",
                    "message": f"Не удалось получить настройки: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка проверки пользователей: {str(e)}"
            }
    
    def test_api_access_methods(self) -> Dict:
        """Тестирование различных методов доступа к API"""
        results = {}
        
        # 1. Тест доступа к /rest/workflows без аутентификации
        try:
            response = self.session.get(f"{self.base_url}/rest/workflows")
            results["rest_workflows_no_auth"] = {
                "status_code": response.status_code,
                "accessible": response.status_code == 200,
                "response_sample": response.text[:100] if response.text else "empty"
            }
        except Exception as e:
            results["rest_workflows_no_auth"] = {
                "error": str(e)
            }
        
        # 2. Тест доступа к /api/v1 (public API)
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows")
            results["public_api_workflows"] = {
                "status_code": response.status_code,
                "accessible": response.status_code == 200,
                "response_sample": response.text[:100] if response.text else "empty"
            }
        except Exception as e:
            results["public_api_workflows"] = {
                "error": str(e)
            }
        
        # 3. Тест node-types endpoint
        try:
            response = self.session.get(f"{self.base_url}/types/nodes.json")
            results["node_types"] = {
                "status_code": response.status_code,
                "accessible": response.status_code == 200,
                "response_sample": response.text[:100] if response.text else "empty"
            }
        except Exception as e:
            results["node_types"] = {
                "error": str(e)
            }
        
        return {
            "status": "success",
            "test_results": results,
            "summary": self._analyze_api_access(results)
        }
    
    def _analyze_api_access(self, results: Dict) -> Dict:
        """Анализ результатов тестирования API"""
        accessible_endpoints = []
        restricted_endpoints = []
        
        for endpoint, result in results.items():
            if result.get('accessible', False):
                accessible_endpoints.append(endpoint)
            else:
                restricted_endpoints.append(endpoint)
        
        return {
            "accessible_count": len(accessible_endpoints),
            "restricted_count": len(restricted_endpoints),
            "accessible_endpoints": accessible_endpoints,
            "restricted_endpoints": restricted_endpoints,
            "api_access_level": "full" if len(accessible_endpoints) > 1 else "limited" if len(accessible_endpoints) == 1 else "none"
        }
    
    def generate_setup_guide(self) -> str:
        """Генерация пошагового руководства по настройке"""
        
        # Проверяем текущий статус
        status = self.check_n8n_status()
        user_check = self.check_if_user_exists()
        api_test = self.test_api_access_methods()
        
        guide = f"""
# 🛠️ ПОШАГОВАЯ НАСТРОЙКА N8N для N8N-Agent

**Время:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**URL:** {self.base_url}

## 📊 ТЕКУЩИЙ СТАТУС

### N8N Статус:
- **Доступность:** {'✅ Работает' if status.get('status') == 'success' else '❌ Недоступен'}
- **Health Check:** {'✅ OK' if status.get('health') == 'ok' else '❌ Проблема'}
- **Веб-интерфейс:** {'✅ Доступен' if status.get('web_accessible') else '❌ Недоступен'}

### Настройка пользователей:
- **Требуется setup:** {'✅ Да' if user_check.get('needs_setup') else '❌ Нет'}
- **User Management:** {'✅ Включен' if user_check.get('user_management_enabled') else '❌ Отключен'}

### API Доступ:
- **Уровень доступа:** {api_test.get('summary', {}).get('api_access_level', 'unknown')}
- **Доступных endpoints:** {api_test.get('summary', {}).get('accessible_count', 0)}
- **Ограниченных endpoints:** {api_test.get('summary', {}).get('restricted_count', 0)}

---

## 🚀 ПОШАГОВЫЕ ИНСТРУКЦИИ

### Шаг 1: Открытие n8n в браузере
1. Перейдите по ссылке: **{self.base_url}**
2. Если появляется ошибка - обновите страницу

### Шаг 2: Первоначальная настройка
"""
        
        if user_check.get('needs_setup'):
            guide += """
**Первый запуск n8n - нужна регистрация:**

1. 👤 **Создайте владельца аккаунта:**
   - Email: `admin@n8n-agent.local`
   - Пароль: `N8NAgent2025!`
   - Имя: `N8N Agent Admin`

2. 🏢 **Настройки экземпляра:**
   - Использование: `Personal`
   - Цель: `Automation & Integration`

3. ✅ **Завершите setup**

"""
        else:
            guide += """
**n8n уже настроен:**
- Войдите в существующий аккаунт
- Или создайте новый аккаунт для N8N-Agent

"""
        
        guide += f"""
### Шаг 3: Получение API доступа

#### Метод 1: API Ключ (Рекомендуется)
1. В n8n перейдите в **Settings** → **API**
2. Создайте новый **API Key**
3. Скопируйте ключ и сохраните в файл .env:
   ```
   N8N_API_KEY=your_api_key_here
   ```

#### Метод 2: Email/Password аутентификация
1. Используйте данные аккаунта для входа через API
2. Обновите .env файл:
   ```
   N8N_EMAIL=admin@n8n-agent.local
   N8N_PASSWORD=your_secure_password_here
   ```

### Шаг 4: Тестирование подключения
После получения API доступа выполните:
```bash
cd /Users/hdv_1987/Desktop/Projects/N8N-Agent
python3 core/n8n_enhanced_api_client.py
```

---

## 🔧 TROUBLESHOOTING

### Проблема: "Secure Cookie" ошибка
**Решение:** Уже исправлено с помощью `N8N_SECURE_COOKIE=false`

### Проблема: API возвращает 401 Unauthorized
**Решение:** 
1. Убедитесь что прошли регистрацию
2. Получите API ключ или используйте email/password

### Проблема: 404 на /rest/node-types
**Решение:** Попробуйте альтернативные endpoints:
- `/types/nodes.json`
- `/rest/node-types` (после аутентификации)

---

## 📋 ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] n8n открывается в браузере
- [ ] Пройдена регистрация / вход
- [ ] Получен API ключ ИЛИ настроена email аутентификация  
- [ ] Обновлен .env файл
- [ ] API тестирование прошло успешно
- [ ] Доступ к workflow и node-types работает

**После завершения всех пунктов - готовы к ФАЗЕ 2! 🚀**

---

*Руководство создано N8N Setup Assistant v1.0*
"""
        
        return guide

def main():
    """Главная функция Setup Assistant"""
    
    print("🛠️ Запуск N8N Setup Assistant...")
    
    assistant = N8NSetupAssistant()
    
    # Проверяем статус
    status = assistant.check_n8n_status()
    
    if status['status'] == 'success':
        print("✅ n8n работает корректно!")
        
        # Открываем в браузере
        assistant.open_n8n_in_browser()
        
        # Генерируем руководство
        guide = assistant.generate_setup_guide()
        
        # Сохраняем руководство
        guide_path = "/Users/hdv_1987/Desktop/Projects/N8N-Agent/N8N_SETUP_GUIDE.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"\n📖 Руководство сохранено: {guide_path}")
        print("\n" + guide)
        
    else:
        print(f"❌ Проблема с n8n: {status['message']}")
        print("🔧 Попробуйте перезапустить n8n контейнер")

if __name__ == "__main__":
    main()
