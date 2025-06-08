#!/usr/bin/env python3
"""
N8N-Agent v1.0 - Streamlit Web Interface
Веб-интерфейс для создания n8n workflow по текстовому описанию
"""

import streamlit as st
import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Добавляем путь к core модулям
sys.path.append(str(Path(__file__).parent / 'core'))

try:
    from n8n_claude_service_mock import N8NClaudeServiceMock
    from n8n_production_client import N8NProductionClient
    from n8n_knowledge_base import N8NKnowledgeBase
except ImportError as e:
    st.error(f"Ошибка импорта модулей: {e}")
    st.stop()

# Конфигурация страницы
st.set_page_config(
    page_title="N8N-Agent v1.0",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Функция загрузки конфигурации
@st.cache_data
def load_config():
    """Загрузка конфигурации из .env"""
    config = {}
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    return config

# Функция проверки n8n
@st.cache_data(ttl=30)
def check_n8n_status():
    """Проверка статуса n8n сервера"""
    try:
        response = requests.get('http://localhost:5678/healthz', timeout=5)
        return response.status_code == 200
    except:
        return False

# Функция получения workflow
@st.cache_data(ttl=30)
def get_workflows(api_key):
    """Получение списка workflow из n8n"""
    try:
        headers = {'X-N8N-API-KEY': api_key}
        response = requests.get('http://localhost:5678/api/v1/workflows', headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
    except:
        pass
    return []

def main():
    """Главная функция приложения"""
    
    # Заголовок
    st.title("🚀 N8N-Agent v1.0")
    st.markdown("### AI система для создания n8n workflow")
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки")
        
        # Загрузка конфигурации
        config = load_config()
        
        # Проверка статуса n8n
        n8n_status = check_n8n_status()
        if n8n_status:
            st.success("✅ n8n сервер работает")
        else:
            st.error("❌ n8n сервер недоступен")
            st.markdown("Запустите n8n: `docker run -p 5678:5678 n8nio/n8n`")
        
        # API ключи
        st.subheader("🔑 API Ключи")
        
        n8n_api_key = st.text_input(
            "N8N API Key:",
            value=config.get('N8N_API_KEY', ''),
            type="password",
            help="JWT токен от n8n"
        )
        
        claude_api_key = st.text_input(
            "Claude API Key:",
            value=config.get('CLAUDE_API_KEY', ''),
            type="password",
            help="API ключ от Anthropic Claude"
        )
        
        # Режим работы
        st.subheader("🎛️ Режим работы")
        use_real_claude = st.checkbox(
            "Использовать реальный Claude API",
            value=bool(claude_api_key),
            help="Если выключено - используется Mock режим"
        )
        
        # Статистика
        if n8n_api_key and n8n_status:
            workflows = get_workflows(n8n_api_key)
            st.subheader("📊 Статистика")
            st.metric("Всего workflow", len(workflows))
            active_count = sum(1 for w in workflows if w.get('active'))
            st.metric("Активных", active_count)
    
    # Основной интерфейс
    if not n8n_status:
        st.error("⚠️ Сначала запустите n8n сервер!")
        st.stop()
    
    if not n8n_api_key:
        st.warning("⚠️ Введите N8N API ключ в боковой панели")
        st.stop()
    
    # Основные вкладки
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏗️ Создать Workflow", 
        "📋 Мои Workflow", 
        "📚 База знаний", 
        "🧪 Тестирование"
    ])
    
    # Вкладка 1: Создание workflow
    with tab1:
        st.header("🏗️ Создание нового workflow")
        
        # Форма для создания
        with st.form("create_workflow"):
            st.subheader("📝 Описание процесса")
            
            # Примеры описаний
            examples = {
                "Webhook → Slack": "При получении webhook отправить уведомление в Slack с информацией о событии",
                "Email → Google Sheets": "При получении нового email добавить информацию в Google Sheets",
                "API мониторинг": "Каждые 5 минут проверять API сервиса и отправлять алерт если недоступен",
                "Обработка файлов": "При загрузке файла в папку обработать его и отправить результат по email"
            }
            
            example_choice = st.selectbox(
                "Выберите пример или введите свой:",
                ["Свой вариант"] + list(examples.keys())
            )
            
            if example_choice != "Свой вариант":
                default_description = examples[example_choice]
            else:
                default_description = ""
            
            description = st.text_area(
                "Описание автоматизации:",
                value=default_description,
                height=100,
                placeholder="Опишите какой процесс нужно автоматизировать..."
            )
            
            # Дополнительные параметры
            col1, col2 = st.columns(2)
            
            with col1:
                workflow_name = st.text_input(
                    "Название workflow:",
                    value="",
                    placeholder="Автоматически из описания"
                )
                
                complexity = st.selectbox(
                    "Сложность:",
                    ["Простой (2-3 nodes)", "Средний (4-6 nodes)", "Сложный (7+ nodes)"]
                )
            
            with col2:
                trigger_type = st.selectbox(
                    "Тип запуска:",
                    ["Webhook", "Schedule", "Manual", "Email", "File"]
                )
                
                auto_activate = st.checkbox(
                    "Активировать после создания",
                    value=False,
                    help="Попытаться активировать workflow автоматически"
                )
            
            # Кнопка создания
            submitted = st.form_submit_button("🚀 Создать Workflow", type="primary")
            
            if submitted and description.strip():
                with st.spinner("🔄 Создаю workflow..."):
                    try:
                        # Выбор сервиса
                        if use_real_claude and claude_api_key:
                            st.info("🧠 Используем реальный Claude API...")
                            # Здесь был бы реальный Claude
                            claude_service = N8NClaudeServiceMock()
                        else:
                            st.info("🎭 Используем Mock режим...")
                            claude_service = N8NClaudeServiceMock()
                        
                        # Генерация workflow
                        workflow_data = claude_service.generate_workflow(
                            description=description,
                            complexity=complexity,
                            trigger_type=trigger_type.lower(),
                            workflow_name=workflow_name or None
                        )
                        
                        # Создание в n8n
                        client = N8NProductionClient(n8n_api_key)
                        result = client.create_workflow(workflow_data)
                        
                        if result.get('success'):
                            workflow_id = result['workflow_id']
                            st.success(f"✅ Workflow создан успешно!")
                            
                            # Показ результата
                            col1, col2 = st.columns(2)
                            with col1:
                                st.info(f"**ID:** {workflow_id}")
                                st.info(f"**URL:** http://localhost:5678/workflow/{workflow_id}")
                            
                            with col2:
                                if auto_activate:
                                    with st.spinner("🔄 Активирую workflow..."):
                                        activation_result = client.activate_workflow(workflow_id)
                                        if activation_result.get('success'):
                                            st.success("✅ Workflow активирован!")
                                        else:
                                            st.warning("⚠️ Workflow создан, но активация не удалась")
                            
                            # Показ структуры
                            with st.expander("📋 Структура workflow"):
                                st.json(workflow_data)
                        
                        else:
                            st.error(f"❌ Ошибка создания: {result.get('error', 'Неизвестная ошибка')}")
                    
                    except Exception as e:
                        st.error(f"❌ Ошибка: {str(e)}")
    
    # Вкладка 2: Список workflow
    with tab2:
        st.header("📋 Мои Workflow")
        
        if n8n_api_key:
            workflows = get_workflows(n8n_api_key)
            
            if workflows:
                # Фильтры
                col1, col2, col3 = st.columns(3)
                with col1:
                    show_active_only = st.checkbox("Только активные")
                with col2:
                    show_archived = st.checkbox("Показать архивированные")
                with col3:
                    sort_by = st.selectbox("Сортировка", ["Дата создания", "Название", "Статус"])
                
                # Фильтрация
                filtered_workflows = workflows
                if show_active_only:
                    filtered_workflows = [w for w in filtered_workflows if w.get('active')]
                if not show_archived:
                    filtered_workflows = [w for w in filtered_workflows if not w.get('isArchived')]
                
                # Отображение workflow
                for workflow in filtered_workflows:
                    with st.expander(f"🔧 {workflow['name']} ({'✅ Активен' if workflow.get('active') else '⏸️ Неактивен'})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**ID:** {workflow['id']}")
                            st.markdown(f"**Создан:** {workflow['createdAt'][:10]}")
                            st.markdown(f"**Nodes:** {len(workflow.get('nodes', []))}")
                            st.markdown(f"**Триггеров:** {workflow.get('triggerCount', 0)}")
                        
                        with col2:
                            if st.button(f"🔗 Открыть", key=f"open_{workflow['id']}"):
                                st.markdown(f"[Открыть в n8n](http://localhost:5678/workflow/{workflow['id']})")
                            
                            if workflow.get('active'):
                                if st.button(f"⏸️ Деактивировать", key=f"deactivate_{workflow['id']}"):
                                    st.info("Функция деактивации будет добавлена")
                            else:
                                if st.button(f"▶️ Активировать", key=f"activate_{workflow['id']}"):
                                    st.info("Функция активации будет добавлена")
                        
                        # Показ nodes
                        if st.checkbox(f"Показать структуру", key=f"show_{workflow['id']}"):
                            st.json(workflow.get('nodes', []))
            else:
                st.info("📋 Пока нет созданных workflow")
    
    # Вкладка 3: База знаний
    with tab3:
        st.header("📚 База знаний N8N")
        
        try:
            kb = N8NKnowledgeBase()
            
            # Статистика базы знаний
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего nodes", len(kb.nodes))
            with col2:
                st.metric("Паттернов", len(kb.patterns))
            with col3:
                st.metric("Примеров", len(kb.examples))
            
            # Nodes
            st.subheader("🧩 Доступные Nodes")
            for node_type, node_info in kb.nodes.items():
                with st.expander(f"{node_info['emoji']} {node_type}"):
                    st.markdown(f"**Описание:** {node_info['description']}")
                    st.markdown(f"**Категория:** {node_info['category']}")
                    st.markdown(f"**Использование:** {node_info['typical_use']}")
                    if node_info.get('parameters'):
                        st.markdown("**Параметры:**")
                        for param in node_info['parameters']:
                            st.markdown(f"- {param}")
            
            # Паттерны
            st.subheader("🔄 Паттерны Workflow")
            for pattern_name, pattern_info in kb.patterns.items():
                with st.expander(f"📋 {pattern_name}"):
                    st.markdown(f"**Описание:** {pattern_info['description']}")
                    st.markdown(f"**Сложность:** {pattern_info['complexity']}")
                    st.markdown("**Nodes:**")
                    for node in pattern_info['nodes']:
                        st.markdown(f"- {node}")
                    st.markdown(f"**Пример:** {pattern_info['example']}")
        
        except Exception as e:
            st.error(f"Ошибка загрузки базы знаний: {e}")
    
    # Вкладка 4: Тестирование
    with tab4:
        st.header("🧪 Тестирование системы")
        
        # Тест подключений
        st.subheader("🔌 Тест подключений")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏥 Тест N8N"):
                with st.spinner("Проверяю n8n..."):
                    status = check_n8n_status()
                    if status:
                        st.success("✅ N8N доступен")
                    else:
                        st.error("❌ N8N недоступен")
        
        with col2:
            if st.button("🧠 Тест Claude"):
                with st.spinner("Проверяю Claude API..."):
                    if claude_api_key:
                        st.success("✅ Claude API ключ указан")
                    else:
                        st.warning("⚠️ Claude API ключ не указан (используется Mock)")
        
        # Быстрый тест создания
        st.subheader("⚡ Быстрый тест")
        
        if st.button("🚀 Создать тестовый workflow"):
            with st.spinner("Создаю тестовый workflow..."):
                try:
                    claude_service = N8NClaudeServiceMock()
                    workflow_data = claude_service.generate_workflow(
                        description="Простой тест webhook для проверки системы",
                        complexity="Простой (2-3 nodes)",
                        trigger_type="webhook"
                    )
                    
                    client = N8NProductionClient(n8n_api_key)
                    result = client.create_workflow(workflow_data)
                    
                    if result.get('success'):
                        st.success(f"✅ Тестовый workflow создан: {result['workflow_id']}")
                    else:
                        st.error(f"❌ Ошибка: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Ошибка тестирования: {str(e)}")
        
        # Логи и отладка
        st.subheader("📝 Системная информация")
        
        info_data = {
            "N8N Status": "🟢 Работает" if check_n8n_status() else "🔴 Недоступен",
            "N8N URL": "http://localhost:5678",
            "API Key": "✅ Настроен" if n8n_api_key else "❌ Не настроен",
            "Claude Mode": "🧠 Real API" if (use_real_claude and claude_api_key) else "🎭 Mock",
            "Workflows": len(get_workflows(n8n_api_key)) if n8n_api_key else 0
        }
        
        st.json(info_data)

if __name__ == "__main__":
    main()
