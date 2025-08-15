"""
Запуск улучшенного Telegram бота для магистратуры ITMO
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем src в путь для импортов
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from maga.config import config
from maga.telegram_bot import ITMOTelegramBot

# Настраиваем логирование
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[logging.StreamHandler(), logging.FileHandler('bot.log', encoding='utf-8')],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Основная функция запуска бота"""
    print('🚀 Запуск улучшенного чат-бота для магистратуры ITMO...')

    # Проверяем конфигурацию
    if not config.validate():
        sys.exit(1)

    # Выводим информацию о конфигурации
    config.print_info()

    try:
        # Создаем и запускаем бота
        if config.TELEGRAM_TOKEN is None:
            logger.error('TELEGRAM_TOKEN не установлен')
            sys.exit(1)

        bot = ITMOTelegramBot(config.TELEGRAM_TOKEN)

        print('📚 Загружаем данные о программах...')

        # Программы будут загружены при первом обращении пользователя
        print('✅ Бот готов к работе! Программы будут загружены автоматически.')

        print('\n🤖 Запускаем Telegram бота...')
        print('   Для остановки нажмите Ctrl+C')
        print('\n📱 Функции бота:')
        print('   • 📊 Сравнение программ')
        print('   • 💡 Персонализированные рекомендации')
        print('   • 🎯 Детальная информация о программах')
        print('   • 💼 Карьерные пути')
        print('   • 🎓 Информация о поступлении')
        print('   • ❓ Интерактивная справка')

        # Запускаем бота
        bot.run()

    except KeyboardInterrupt:
        print('\n🛑 Бот остановлен пользователем')
    except Exception as e:
        logger.error(f'❌ Ошибка при запуске бота: {e}')
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n🛑 Программа остановлена')
    except Exception as e:
        print(f'❌ Критическая ошибка: {e}')
        sys.exit(1)
