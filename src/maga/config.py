"""
Конфигурация для чат-бота магистратуры
"""

import os

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Config:
    """Конфигурация приложения"""

    # Telegram Bot Token
    TELEGRAM_TOKEN: str | None = os.getenv('TELEGRAM_BOT_TOKEN')

    # URLs для парсинга
    AI_PROGRAM_URL = 'https://abit.itmo.ru/program/master/ai'
    AI_PRODUCT_PROGRAM_URL = 'https://abit.itmo.ru/program/master/ai_product'

    # Настройки парсера
    PARSER_TIMEOUT = 30  # секунды
    PARSER_RETRY_COUNT = 3

    # Настройки логирования
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Настройки бота
    BOT_COMMAND_TIMEOUT = 60  # секунды
    MAX_MESSAGE_LENGTH = 4096  # максимальная длина сообщения в Telegram

    # Настройки анализа
    MAX_COURSES_DISPLAY = 10  # максимальное количество курсов для отображения
    RECOMMENDATION_TOP_N = 3  # количество топ рекомендаций

    # Константы для валидации
    MIN_TOKEN_LENGTH = 10

    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность конфигурации"""
        if not cls.TELEGRAM_TOKEN:
            print('❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в переменных окружения')
            print('   Создайте файл .env и добавьте: TELEGRAM_BOT_TOKEN=your_token_here')
            return False

        if len(cls.TELEGRAM_TOKEN) < cls.MIN_TOKEN_LENGTH:
            print('❌ Ошибка: Неверный формат TELEGRAM_BOT_TOKEN')
            print(
                f'   Токен должен быть непустой строкой длиной не менее {cls.MIN_TOKEN_LENGTH} символов'
            )
            return False

        print('✅ Конфигурация валидна')
        return True

    @classmethod
    def print_info(cls) -> None:
        """Выводит информацию о конфигурации"""
        print('📋 Конфигурация чат-бота:')
        print(
            f"   • Telegram Token: {'*' * 10 + cls.TELEGRAM_TOKEN[-4:] if cls.TELEGRAM_TOKEN else 'Не установлен'}"
        )
        print(f'   • AI Program URL: {cls.AI_PROGRAM_URL}')
        print(f'   • AI Product Program URL: {cls.AI_PRODUCT_PROGRAM_URL}')
        print(f'   • Parser Timeout: {cls.PARSER_TIMEOUT}s')
        print(f'   • Log Level: {cls.LOG_LEVEL}')
        print(f'   • Max Courses Display: {cls.MAX_COURSES_DISPLAY}')
        print(f'   • Recommendation Top N: {cls.RECOMMENDATION_TOP_N}')


# Создаем экземпляр конфигурации
config = Config()
