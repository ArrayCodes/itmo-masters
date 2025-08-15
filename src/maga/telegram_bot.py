"""
Telegram бот для помощи абитуриентам магистратуры ITMO
"""

import asyncio
import logging

from program_analyzer import ProgramAnalyzer
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from web_parser import ITMOWebParser, Program

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING_ACTION, ENTERING_BACKGROUND, CHOOSING_PROGRAM = range(3)


class ITMOTelegramBot:
    """Telegram бот для анализа программ магистратуры ИТМО"""

    # Константы для магических чисел
    MAX_MESSAGE_LENGTH = 4096
    MAX_COURSES_DISPLAY = 10

    def __init__(self, token: str) -> None:
        """Инициализация бота"""
        self.token = token
        self.application = Application.builder().token(token).build()
        self.programs: list[Program] | None = None
        self.analyzer: ProgramAnalyzer | None = None
        self.user_states: dict[int, dict] = {}
        self.user_backgrounds: dict[int, str] = {}
        self.user_program_selections: dict[int, str] = {}
        self.user_career_selections: dict[int, str] = {}
        self.user_admission_selections: dict[int, str] = {}

        # Регистрируем обработчики
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def _load_programs(self) -> None:
        """Загружает данные о программах"""
        try:
            async with ITMOWebParser() as parser:
                # Загружаем страницы программ
                ai_html = await parser.fetch_page('https://abit.itmo.ru/program/master/ai')
                ai_product_html = await parser.fetch_page(
                    'https://abit.itmo.ru/program/master/ai_product'
                )

                if ai_html and ai_product_html:
                    # Парсим программы
                    ai_program = parser.parse_ai_program(ai_html)
                    ai_product_program = parser.parse_ai_product_program(ai_product_html)

                    self.programs = [ai_program, ai_product_program]
                    self.analyzer = ProgramAnalyzer(self.programs)

                    logger.info(f'Загружено {len(self.programs)} программ')
                else:
                    logger.error('Не удалось загрузить страницы программ')

        except Exception as e:
            logger.error(f'Ошибка при загрузке программ: {e}')

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработчик команды /start"""
        user_id = update.effective_user.id

        # Сбрасываем состояние пользователя
        self.user_states[user_id] = {}

        # Загружаем данные о программах, если они еще не загружены
        if not self.programs:
            await update.message.reply_text('📚 Загружаю данные о программах...')
            await self._load_programs()
            if self.programs:
                await update.message.reply_text(f'✅ Загружено {len(self.programs)} программ!')
            else:
                await update.message.reply_text('⚠️ Не удалось загрузить данные о программах')

        welcome_text = """
🎓 Добро пожаловать в чат-бот для абитуриентов магистратуры ITMO!

Я помогу вам разобраться в магистерских программах и дам персонализированные рекомендации по выбору дисциплин.

📚 Доступные программы:
• Искусственный интеллект
• AI Product Management

💬 Что вы хотите узнать?
        """

        keyboard = [
            [InlineKeyboardButton('📊 Сравнить программы', callback_data='compare')],
            [InlineKeyboardButton('💡 Получить рекомендации', callback_data='recommend')],
            [InlineKeyboardButton('🎯 Информация о программе', callback_data='program_info')],
            [InlineKeyboardButton('💼 Карьерные пути', callback_data='career')],
            [InlineKeyboardButton('🎓 Как поступить', callback_data='admission')],
            [InlineKeyboardButton('❓ Помощь', callback_data='help')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text.strip(), reply_markup=reply_markup)

        return CHOOSING_ACTION

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        help_text = """
❓ Справка по использованию бота:

📚 Основные функции:
• /start - Главное меню
• /help - Эта справка

🎯 Что умеет бот:
• 📊 Сравнивать программы магистратуры
• 💡 Давать персонализированные рекомендации
• 🎯 Показывать детальную информацию о программах
• 💼 Рассказывать о карьерных путях
• 🎓 Информировать о поступлении

💡 Как получить рекомендации:
1. Выберите "Получить рекомендации"
2. Опишите ваш бэкграунд (опыт, образование, навыки)
3. Получите персонализированные советы

🔍 Примеры описания бэкграунда:
• "У меня есть опыт в программировании на Python и математике"
• "Я работаю в сфере бизнеса и менеджмента"
• "У меня техническое образование и опыт в разработке"
        """
        
        await update.message.reply_text(help_text.strip())

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        if query.data == 'compare':
            await self._handle_compare(query)
        elif query.data == 'recommend':
            await self._handle_recommend_start(query)
        elif query.data == 'program_info':
            await self._handle_program_info_start(query)
        elif query.data == 'career':
            await self._handle_career_start(query)
        elif query.data == 'admission':
            await self._handle_admission_start(query)
        elif query.data == 'help':
            await self._handle_help(query)
        elif query.data.startswith('program_'):
            await self._handle_program_selection(query)
        elif query.data.startswith('career_'):
            await self._handle_career_program(query)
        elif query.data.startswith('admission_'):
            await self._handle_admission_program(query)
        elif query.data == 'back_to_main':
            await self._back_to_main_menu(query)

    async def _handle_compare(self, query: CallbackQuery) -> None:
        """Обрабатывает запрос на сравнение программ"""
        # Проверяем, загружены ли данные
        if not self.programs or not self.analyzer:
            await query.edit_message_text('📚 Загружаю данные о программах...')
            await self._load_programs()
            if not self.programs or not self.analyzer:
                await query.edit_message_text('❌ Не удалось загрузить данные о программах')
                return
            await query.edit_message_text('✅ Данные загружены! Формирую сравнение...')

        comparison = self.analyzer.get_program_comparison()

        # Разбиваем на части, если сообщение слишком длинное
        if len(comparison) > self.MAX_MESSAGE_LENGTH:
            parts = [
                comparison[i : i + self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(comparison), self.MAX_MESSAGE_LENGTH)
            ]
            for i, part in enumerate(parts):
                if i == 0:
                    await query.edit_message_text(part)
                else:
                    await query.message.reply_text(part)
        else:
            await query.edit_message_text(comparison)

        await self._show_back_button(query)

    async def _handle_recommend_start(self, query: CallbackQuery) -> int:
        """Начинает процесс получения рекомендаций"""
        # Проверяем, загружены ли данные
        if not self.programs or not self.analyzer:
            await query.edit_message_text('📚 Загружаю данные о программах...')
            await self._load_programs()
            if not self.programs or not self.analyzer:
                await query.edit_message_text('❌ Не удалось загрузить данные о программах')
                return

        user_id = query.from_user.id
        logger.info(f'Начинаем процесс рекомендаций для пользователя {user_id}')

        # Всегда запрашиваем бэкграунд (не запоминаем предыдущий)
        logger.info(f'Запрашиваем бэкграунд у пользователя {user_id}')

        # Запрашиваем бэкграунд
        await query.edit_message_text(
            '📝 Расскажите о вашем бэкграунде, чтобы получить персонализированные рекомендации!\n\n'
            'Например:\n'
            "• 'У меня есть опыт в программировании на Python и математике'\n"
            "• 'Я работаю в сфере бизнеса и менеджмента'\n"
            "• 'У меня техническое образование и опыт в разработке'\n\n"
            'Отправьте сообщение с описанием вашего опыта:'
        )

        self.user_states[user_id] = {'action': 'waiting_background'}
        logger.info(f"Установлено состояние 'waiting_background' для пользователя {user_id}")
        logger.info('Возвращаем состояние ENTERING_BACKGROUND')
        return ENTERING_BACKGROUND

    async def _handle_program_info_start(self, query: CallbackQuery) -> None:
        """Начинает процесс получения информации о программе"""
        keyboard = [
            [InlineKeyboardButton('Искусственный интеллект', callback_data='program_ai')],
            [InlineKeyboardButton('AI Product Management', callback_data='program_ai_product')],
            [InlineKeyboardButton('🔙 Назад', callback_data='back_to_main')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            '🎯 Выберите программу для получения подробной информации:', reply_markup=reply_markup
        )

    async def _handle_career_start(self, query: CallbackQuery) -> None:
        """Начинает процесс получения информации о карьере"""
        keyboard = [
            [InlineKeyboardButton('Искусственный интеллект', callback_data='career_ai')],
            [InlineKeyboardButton('AI Product Management', callback_data='career_ai_product')],
            [InlineKeyboardButton('🔙 Назад', callback_data='back_to_main')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            '💼 Выберите программу для получения информации о карьерных путях:',
            reply_markup=reply_markup,
        )

    async def _handle_admission_start(self, query: CallbackQuery) -> None:
        """Начинает процесс получения информации о поступлении"""
        keyboard = [
            [InlineKeyboardButton('Искусственный интеллект', callback_data='admission_ai')],
            [InlineKeyboardButton('AI Product Management', callback_data='admission_ai_product')],
            [InlineKeyboardButton('🔙 Назад', callback_data='back_to_main')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            '🎓 Выберите программу для получения информации о поступлении:',
            reply_markup=reply_markup,
        )

    async def _handle_program_selection(self, query):
        """Обрабатывает выбор программы для получения информации"""
        program_name = query.data.replace('program_', '')

        if program_name == 'ai':
            program_display_name = 'Искусственный интеллект'
        elif program_name == 'ai_product':
            program_display_name = 'AI Product Management'
        else:
            await query.edit_message_text('❌ Программа не найдена')
            return

        if not self.analyzer:
            await query.edit_message_text(
                '⏳ Данные о программах еще загружаются. Попробуйте позже.'
            )
            return

        info = self.analyzer.get_detailed_program_info(program_display_name)

        # Разбиваем на части, если сообщение слишком длинное
        if len(info) > self.MAX_MESSAGE_LENGTH:
            parts = [
                info[i : i + self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(info), self.MAX_MESSAGE_LENGTH)
            ]
            for i, part in enumerate(parts):
                if i == 0:
                    await query.edit_message_text(part)
                else:
                    await query.message.reply_text(part)
        else:
            await query.edit_message_text(info)

        await self._show_back_button(query)

    async def _handle_career_program(self, query):
        """Обрабатывает запрос на информацию о карьере для конкретной программы"""
        program_name = query.data.replace('career_', '')

        if program_name == 'ai':
            program_display_name = 'Искусственный интеллект'
        elif program_name == 'ai_product':
            program_display_name = 'AI Product Management'
        else:
            await query.edit_message_text('❌ Программа не найдена')
            return

        if not self.analyzer:
            await query.edit_message_text(
                '⏳ Данные о программах еще загружаются. Попробуйте позже.'
            )
            return

        career_info = self.analyzer.get_career_paths(program_display_name)

        await query.edit_message_text(career_info)
        await self._show_back_button(query)

    async def _handle_admission_program(self, query):
        """Обрабатывает запрос на информацию о поступлении для конкретной программы"""
        program_name = query.data.replace('admission_', '')

        if program_name == 'ai':
            program_display_name = 'Искусственный интеллект'
        elif program_name == 'ai_product':
            program_display_name = 'AI Product Management'
        else:
            await query.edit_message_text('❌ Программа не найдена')
            return

        if not self.analyzer:
            await query.edit_message_text(
                '⏳ Данные о программах еще загружаются. Попробуйте позже.'
            )
            return

        admission_info = self.analyzer.get_admission_info(program_display_name)

        # Разбиваем на части, если сообщение слишком длинное
        if len(admission_info) > self.MAX_MESSAGE_LENGTH:
            parts = [
                admission_info[i : i + self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(admission_info), self.MAX_MESSAGE_LENGTH)
            ]
            for i, part in enumerate(parts):
                if i == 0:
                    await query.edit_message_text(part)
                else:
                    await query.message.reply_text(part)
        else:
            await query.edit_message_text(admission_info)

        await self._show_back_button(query)

    async def _handle_help(self, query):
        """Показывает справку"""
        help_text = """
🔍 Как пользоваться ботом:

1️⃣ **Сравнение программ** - получите детальное сравнение всех программ
2️⃣ **Рекомендации** - расскажите о своем бэкграунде и получите персонализированные советы
3️⃣ **Информация о программе** - узнайте подробности о конкретной программе
4️⃣ **Карьерные пути** - узнайте о возможностях трудоустройства
5️⃣ **Как поступить** - получите информацию о способах поступления

💡 **Примеры вопросов:**
• "Какие дисциплины есть в программе ИИ?"
• "Что изучают в AI Product Management?"
• "Какие выборные курсы подойдут для программиста?"
• "Расскажите о программе искусственного интеллекта"

🎯 **Бот поможет вам:**
• Понять различия между программами
• Выбрать подходящие дисциплины
• Спланировать обучение
• Узнать о карьерных перспективах
• Разобраться в процессе поступления
        """

        await query.edit_message_text(help_text.strip())
        await self._show_back_button(query)

    async def _show_recommendations(self, query, background: str):
        """Показывает рекомендации для пользователя (для CallbackQuery)"""
        if not self.analyzer:
            await query.edit_message_text(
                '⏳ Данные о программах еще загружаются. Попробуйте позже.'
            )
            return

        recommendations = self.analyzer.get_course_recommendations(background)

        # Разбиваем на части, если сообщение слишком длинное
        if len(recommendations) > self.MAX_MESSAGE_LENGTH:
            parts = [
                recommendations[i : i + self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(recommendations), self.MAX_MESSAGE_LENGTH)
            ]
            for i, part in enumerate(parts):
                if i == 0:
                    await query.edit_message_text(part)
                else:
                    await query.message.reply_text(part)
        else:
            await query.edit_message_text(recommendations)

        await self._show_back_button(query)

    async def _show_recommendations_for_message(self, update: Update, background: str):
        """Показывает рекомендации для пользователя (для текстовых сообщений)"""
        print(f"🔍 _show_recommendations_for_message вызван с бэкграундом: '{background}'")
        print(f'📊 self.analyzer: {self.analyzer}')
        print(f"📚 self.programs: {len(self.programs) if self.programs else 'None'}")

        if not self.analyzer:
            print('❌ self.analyzer равен None!')
            await update.message.reply_text(
                '⏳ Данные о программах еще загружаются. Попробуйте позже.'
            )
            return

        print(f"✅ Вызываем analyzer.get_course_recommendations('{background}')")
        recommendations = self.analyzer.get_course_recommendations(background)
        print(f'📝 Получены рекомендации длиной: {len(recommendations)}')

        # Разбиваем на части, если сообщение слишком длинное
        if len(recommendations) > self.MAX_MESSAGE_LENGTH:
            parts = [
                recommendations[i : i + self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(recommendations), self.MAX_MESSAGE_LENGTH)
            ]
            for _i, part in enumerate(parts):
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(recommendations)

        # Показываем кнопку возврата в главное меню
        await self._show_back_button_for_message(update)

    async def _show_back_button_for_message(self, update: Update):
        """Показывает кнопку возврата в главное меню (для текстовых сообщений)"""
        keyboard = [[InlineKeyboardButton('🔙 Главное меню', callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text('Выберите следующее действие:', reply_markup=reply_markup)

    async def _show_back_button(self, query):
        """Показывает кнопку возврата в главное меню"""
        keyboard = [[InlineKeyboardButton('🔙 Главное меню', callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text('Выберите следующее действие:', reply_markup=reply_markup)

    async def _back_to_main_menu(self, query):
        """Возвращает в главное меню"""
        # Создаем главное меню для CallbackQuery
        welcome_text = """
🎓 Главное меню чат-бота для абитуриентов магистратуры ITMO!

Я помогу вам разобраться в магистерских программах и дам персонализированные рекомендации по выбору дисциплин.

📚 Доступные программы:
• Искусственный интеллект
• AI Product Management

💬 Что вы хотите узнать?
        """

        keyboard = [
            [InlineKeyboardButton('📊 Сравнить программы', callback_data='compare')],
            [InlineKeyboardButton('💡 Получить рекомендации', callback_data='recommend')],
            [InlineKeyboardButton('🎯 Информация о программе', callback_data='program_info')],
            [InlineKeyboardButton('💼 Карьерные пути', callback_data='career')],
            [InlineKeyboardButton('🎓 Как поступить', callback_data='admission')],
            [InlineKeyboardButton('❓ Помощь', callback_data='help')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(welcome_text.strip(), reply_markup=reply_markup)

        return CHOOSING_ACTION

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text

        logger.info('=== handle_message вызван ===')
        logger.info(f'Получено сообщение от пользователя {user_id}: {text}')
        logger.info(f"Состояние пользователя: {self.user_states.get(user_id, 'не установлено')}")
        logger.info('Текущее состояние ConversationHandler: ENTERING_BACKGROUND')

        # Проверяем состояние пользователя
        print(f'🔍 Проверяем состояние пользователя {user_id}')
        print(f'   user_states: {self.user_states}')
        print(
            f"   action: {self.user_states.get(user_id, {}).get('action') if user_id in self.user_states else 'не установлено'}"
        )

        if (
            user_id in self.user_states
            and self.user_states[user_id].get('action') == 'waiting_background'
        ):
            print(f"✅ Пользователь {user_id} отправляет бэкграунд: '{text}'")
            logger.info(f'Пользователь {user_id} отправляет бэкграунд')

            # Пользователь отправляет бэкграунд (не сохраняем)
            self.user_states[user_id] = {}

            await update.message.reply_text(
                '✅ Спасибо! Анализирую ваш опыт и формирую рекомендации...'
            )

            # Показываем рекомендации
            print('🚀 Вызываем _show_recommendations_for_message')
            await self._show_recommendations_for_message(update, text)
            return CHOOSING_ACTION
        else:
            logger.info(f'Пользователь {user_id} не в состоянии ожидания бэкграунда')

            # Если это не бэкграунд, анализируем вопрос
            response = await self._analyze_question(text)
            await update.message.reply_text(response)

    async def _analyze_question(self, question: str) -> str:
        """Анализирует вопрос и формирует ответ"""
        question_lower = question.lower()

        # Проверяем, загружены ли данные
        if not self.programs:
            return '📚 Данные о программах загружаются автоматически. Попробуйте использовать кнопки меню или подождите немного.'

        # Определяем, о какой программе спрашивают
        program_mentioned = None
        if any(word in question_lower for word in ['ии', 'искусственный интеллект', 'ai']):
            program_mentioned = next(
                (p for p in self.programs if 'искусственный интеллект' in p.name.lower()), None
            )
        elif any(word in question_lower for word in ['продукт', 'product', 'менеджмент']):
            program_mentioned = next(
                (p for p in self.programs if 'product' in p.name.lower()), None
            )

        # Формируем ответ
        if program_mentioned:
            response = f'🎯 {program_mentioned.name}:\n\n'

            if any(word in question_lower for word in ['дисциплина', 'курс', 'предмет', 'изучают']):
                response += '📚 Основные дисциплины:\n'
                for course in program_mentioned.courses[
                    : self.MAX_COURSES_DISPLAY
                ]:  # Показываем первые 10
                    response += (
                        f'• {course.name} ({course.credits} кредитов, {course.semester} семестр)\n'
                    )

                if len(program_mentioned.courses) > self.MAX_COURSES_DISPLAY:
                    response += f'\n... и еще {len(program_mentioned.courses) - self.MAX_COURSES_DISPLAY} дисциплин'
            else:
                response += f'📖 {program_mentioned.description}\n\n'
                response += f'⏱ Длительность: {program_mentioned.duration} семестра\n'
                response += f'🎓 Общее количество кредитов: {program_mentioned.total_credits}'
        else:
            response = (
                '🤔 Я понимаю ваш вопрос, но для более точного ответа уточните, '
                'о какой программе идет речь:\n'
                '• Искусственный интеллект\n'
                '• AI Product Management\n\n'
                'Или используйте кнопки меню для навигации.'
            )

        return response

    def run(self):
        """Запускает бота"""
        # Создаем приложение
        application = Application.builder().token(self.token).build()

        # Создаем ConversationHandler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_command)],
            states={
                CHOOSING_ACTION: [CallbackQueryHandler(self.button_callback)],
                ENTERING_BACKGROUND: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
                ],
            },
            fallbacks=[CommandHandler('start', self.start_command)],
            per_message=False,
            per_chat=True,
        )

        # Добавляем обработчики
        application.add_handler(conv_handler)

        # Добавляем дополнительный обработчик для текстовых сообщений
        # на случай, если ConversationHandler не сработает
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        # Запускаем бота
        application.run_polling()


async def main():
    """Основная функция для тестирования"""
    # Для тестирования используем заглушку токена
    bot = ITMOTelegramBot('YOUR_BOT_TOKEN_HERE')

    # Загружаем данные
    await bot._load_programs()

    print('✅ Бот инициализирован')
    print(f'📚 Загружено программ: {len(bot.programs)}')

    if bot.programs:
        print('\n📊 Сравнение программ:')
        if bot.analyzer:
            print(bot.analyzer.get_program_comparison())


if __name__ == '__main__':
    asyncio.run(main())
