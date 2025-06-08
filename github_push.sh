#!/bin/bash
# GitHub Push Script для N8N-Agent v1.0
# Замените YOUR_USERNAME на ваше GitHub имя пользователя

echo "🚀 Настройка GitHub remote для N8N-Agent v1.0"

# Добавляем remote (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/n8n-agent.git

# Проверяем remote
git remote -v

# Пушим в main ветку
git branch -M main
git push -u origin main

echo "🎉 N8N-Agent v1.0 успешно опубликован на GitHub!"
echo "📋 Не забудьте:"
echo "  1. Обновить README.md с правильным username"
echo "  2. Добавить темы (topics) в настройках репозитория"
echo "  3. Настроить GitHub Pages для документации"
