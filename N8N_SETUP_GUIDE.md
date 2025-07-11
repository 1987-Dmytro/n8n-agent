
# 🛠️ ПОШАГОВАЯ НАСТРОЙКА N8N для N8N-Agent

**Время:** 2025-06-08 09:32:41
**URL:** http://localhost:5678

## 📊 ТЕКУЩИЙ СТАТУС

### N8N Статус:
- **Доступность:** ✅ Работает
- **Health Check:** ✅ OK
- **Веб-интерфейс:** ✅ Доступен

### Настройка пользователей:
- **Требуется setup:** ✅ Да
- **User Management:** ✅ Включен

### API Доступ:
- **Уровень доступа:** limited
- **Доступных endpoints:** 1
- **Ограниченных endpoints:** 2

---

## 🚀 ПОШАГОВЫЕ ИНСТРУКЦИИ

### Шаг 1: Открытие n8n в браузере
1. Перейдите по ссылке: **http://localhost:5678**
2. Если появляется ошибка - обновите страницу

### Шаг 2: Первоначальная настройка

**Первый запуск n8n - нужна регистрация:**

1. 👤 **Создайте владельца аккаунта:**
   - Email: `admin@n8n-agent.local`
   - Пароль: `N8NAgent2025!`
   - Имя: `N8N Agent Admin`

2. 🏢 **Настройки экземпляра:**
   - Использование: `Personal`
   - Цель: `Automation & Integration`

3. ✅ **Завершите setup**


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
   N8N_PASSWORD=N8NAgent2025!
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
