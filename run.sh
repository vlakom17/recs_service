#!/bin/bash

# Корневая директория проекта
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Основной модуль для запуска
MODULE="src.main"

# Путь к интерпретатору Python (например, из виртуального окружения)
PYTHON="python"

# Установка PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT"

# Запуск приложения
echo "Запуск приложения..."
$PYTHON -m $MODULE --config=$PROJECT_ROOT/configs/dev.yml
