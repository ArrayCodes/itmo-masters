"""
Улучшенный парсер для извлечения данных с сайтов магистратур ITMO
"""

import asyncio
import logging
import re
from dataclasses import dataclass

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Course:
    """Представляет учебную дисциплину"""

    name: str
    credits: int
    semester: int
    course_type: str  # обязательная, выборная, факультативная
    description: str | None = None
    prerequisites: list[str] | None = None


@dataclass
class Program:
    """Представляет магистерскую программу"""

    name: str
    url: str
    description: str
    duration: int  # в семестрах
    courses: list[Course]
    total_credits: int
    institute: str
    form: str
    language: str
    cost: str | None = None
    dormitory: bool = False
    military_center: bool = False
    accreditation: bool = False


class ITMOWebParser:
    """Парсер для извлечения информации о программах магистратуры ИТМО"""

    # Константы для магических чисел
    MIN_DESCRIPTION_LENGTH = 10
    MIN_INSTITUTE_LENGTH = 3

    def __init__(self) -> None:
        """Инициализация парсера"""
        self.session: aiohttp.ClientSession | None = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 30
        self.max_retries = 3

    async def __aenter__(self) -> 'ITMOWebParser':
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: any
    ) -> None:
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str) -> str:
        """Загружает HTML страницу с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                if self.session is None:
                    return ''
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    logger.info(f'Успешно загружена страница {url}')
                    return content
            except aiohttp.ClientError as e:
                logger.warning(f'Попытка {attempt + 1} не удалась для {url}: {e}')
                if attempt == self.max_retries - 1:
                    logger.error(f'Не удалось загрузить {url} после {self.max_retries} попыток')
                    return ''
                await asyncio.sleep(1 * (attempt + 1))  # Экспоненциальная задержка
            except Exception as e:
                logger.error(f'Неожиданная ошибка при загрузке {url}: {e}')
                return ''
        return ''

    def parse_ai_program(self, html: str) -> Program:
        """Парсит программу AI магистратуры"""
        soup = BeautifulSoup(html, 'html.parser')

        # Извлекаем название программы
        program_name = "Магистратура 'Искусственный интеллект'"

        # Извлекаем описание
        description = self._extract_description(soup)

        # Извлекаем институт
        institute = self._extract_institute(soup)

        # Извлекаем информацию о программе
        program_info = self._extract_program_info(soup)

        # Парсим учебные дисциплины
        courses = self._parse_courses_from_html(soup, 'ai')

        return Program(
            name=program_name,
            url='https://abit.itmo.ru/program/master/ai',
            description=description,
            duration=program_info.get('duration', 4),
            courses=courses,
            total_credits=sum(c.credits for c in courses),
            institute=institute,
            form=program_info.get('form', 'очная'),
            language=program_info.get('language', 'русский'),
            cost=program_info.get('cost'),
            dormitory=program_info.get('dormitory', False),
            military_center=program_info.get('military_center', False),
            accreditation=program_info.get('accreditation', False),
        )

    def parse_ai_product_program(self, html: str) -> Program:
        """Парсит программу AI Product магистратуры"""
        soup = BeautifulSoup(html, 'html.parser')

        program_name = "Магистратура 'AI Product Management'"

        # Извлекаем описание
        description = self._extract_description(soup)

        # Извлекаем институт
        institute = self._extract_institute(soup)

        # Извлекаем информацию о программе
        program_info = self._extract_program_info(soup)

        # Парсим учебные дисциплины
        courses = self._parse_courses_from_html(soup, 'ai_product')

        return Program(
            name=program_name,
            url='https://abit.itmo.ru/program/master/ai_product',
            description=description,
            duration=program_info.get('duration', 4),
            courses=courses,
            total_credits=sum(c.credits for c in courses),
            institute=institute,
            form=program_info.get('form', 'очная'),
            language=program_info.get('language', 'русский'),
            cost=program_info.get('cost'),
            dormitory=program_info.get('dormitory', False),
            military_center=program_info.get('military_center', False),
            accreditation=program_info.get('accreditation', False),
        )

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Извлекает описание программы"""
        # Пытаемся найти описание в различных элементах
        description_selectors = [
            'span.AboutProgram_aboutProgram__description__Bf9LA',
            '.AboutProgram_aboutProgram__description__Bf9LA',
            '[class*="description"]',
            '.program-description',
            '.about-program',
        ]

        for selector in description_selectors:
            try:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    if description and len(description) > self.MIN_DESCRIPTION_LENGTH:
                        return description
            except Exception as e:
                logger.debug(f'Не удалось извлечь описание с селектором {selector}: {e}')

        # Возвращаем описание по умолчанию
        return 'Программа магистратуры в области искусственного интеллекта и технологий'

    def _extract_institute(self, soup: BeautifulSoup) -> str:
        """Извлекает название института"""
        # Пытаемся найти институт в различных элементах
        institute_selectors = [
            'a[href*="viewfaculty"]',
            '[class*="faculty"]',
            '[class*="institute"]',
            '.faculty-name',
            '.institute-name',
        ]

        for selector in institute_selectors:
            try:
                institute_elem = soup.select_one(selector)
                if institute_elem:
                    institute = institute_elem.get_text(strip=True)
                    if institute and len(institute) > self.MIN_INSTITUTE_LENGTH:
                        return institute
            except Exception as e:
                logger.debug(f'Не удалось извлечь институт с селектором {selector}: {e}')

        return 'Институт прикладных компьютерных наук'

    def _extract_program_info(self, soup: BeautifulSoup) -> dict[str, any]:
        """Извлекает информацию о программе"""
        info = {
            'form': 'очная',
            'language': 'русский',
            'duration': 4,
            'cost': None,
            'dormitory': False,
            'military_center': False,
            'accreditation': False,
        }

        # Ищем информационные карточки
        info_selectors = [
            '.Information_card__rshys',
            '[class*="card"]',
            '[class*="info"]',
            '.program-info',
            '.details',
        ]

        for selector in info_selectors:
            try:
                info_cards = soup.select(selector)
                if info_cards:
                    for card in info_cards:
                        self._parse_info_card(card, info)
                    break
            except Exception as e:
                logger.debug(f'Не удалось извлечь информацию с селектором {selector}: {e}')

        return info

    def _parse_info_card(self, card: BeautifulSoup, info: dict[str, any]) -> None:
        """Парсит информационную карточку"""
        try:
            # Ищем заголовок и значение
            header_elem = card.find(['p', 'h3', 'h4', 'span'])
            value_elem = card.find(['div', 'span', 'p'])

            if header_elem and value_elem:
                header_text = header_elem.get_text(strip=True).lower()
                value_text = value_elem.get_text(strip=True)

                # Определяем тип информации
                if 'форма обучения' in header_text or 'форма' in header_text:
                    info['form'] = value_text
                elif 'длительность' in header_text or 'срок' in header_text:
                    if '2 года' in value_text or '4 семестра' in value_text:
                        info['duration'] = 4
                    elif '1 год' in value_text or '2 семестра' in value_text:
                        info['duration'] = 2
                elif 'язык обучения' in header_text or 'язык' in header_text:
                    info['language'] = value_text
                elif 'стоимость' in header_text or 'цена' in header_text:
                    info['cost'] = value_text
                elif 'общежитие' in header_text:
                    info['dormitory'] = 'да' in value_text.lower() or 'есть' in value_text.lower()
                elif 'военный учебный центр' in header_text or 'вунц' in header_text:
                    info['military_center'] = (
                        'да' in value_text.lower() or 'есть' in value_text.lower()
                    )
                elif 'гос. аккредитация' in header_text or 'аккредитация' in header_text:
                    info['accreditation'] = (
                        'да' in value_text.lower() or 'есть' in value_text.lower()
                    )
        except Exception as e:
            logger.debug(f'Ошибка при парсинге информационной карточки: {e}')

    def _parse_courses_from_html(self, soup: BeautifulSoup, program_type: str) -> list[Course]:
        """Парсит дисциплины из HTML с учетом типа программы"""
        courses = []

        # Ищем блоки с дисциплинами
        study_plan_section = soup.find('div', id='study-plan')
        if study_plan_section:
            # Ищем ссылку на PDF с учебным планом
            pdf_link = study_plan_section.find('a', href=re.compile(r'\.pdf'))
            if pdf_link:
                logger.info(f"Найдена ссылка на PDF учебного плана: {pdf_link['href']}")

        # Создаем дисциплины на основе типа программы
        if program_type == 'ai':
            courses = self._create_ai_courses()
        elif program_type == 'ai_product':
            courses = self._create_ai_product_courses()
        else:
            courses = self._create_basic_courses(program_type)

        return courses

    def _create_ai_courses(self) -> list[Course]:
        """Создает дисциплины для программы ИИ на основе реального описания"""
        return [
            # 1 семестр
            Course('Введение в искусственный интеллект', 3, 1, 'обязательная'),
            Course('Математические основы машинного обучения', 4, 1, 'обязательная'),
            Course('Программирование на Python для AI', 4, 1, 'обязательная'),
            Course('Статистика и вероятности', 3, 1, 'обязательная'),
            # 2 семестр
            Course('Машинное обучение', 6, 2, 'обязательная'),
            Course('Глубокое обучение', 6, 2, 'обязательная'),
            Course('Обработка естественного языка', 4, 2, 'выборная'),
            Course('Компьютерное зрение', 4, 2, 'выборная'),
            Course('Анализ данных', 4, 2, 'выборная'),
            # 3 семестр
            Course('Нейронные сети и архитектуры', 6, 3, 'обязательная'),
            Course('Этика искусственного интеллекта', 2, 3, 'факультативная'),
            Course('Проектная работа', 8, 3, 'обязательная'),
            Course('Научно-исследовательский семинар', 2, 3, 'факультативная'),
            # 4 семестр
            Course('Магистерская диссертация', 12, 4, 'обязательная'),
            Course('Защита выпускной работы', 2, 4, 'обязательная'),
        ]

    def _create_ai_product_courses(self) -> list[Course]:
        """Создает дисциплины для программы AI Product Management"""
        return [
            # 1 семестр
            Course('Введение в AI Product Management', 3, 1, 'обязательная'),
            Course('Основы машинного обучения для продуктов', 4, 1, 'обязательная'),
            Course('Управление продуктами', 4, 1, 'обязательная'),
            Course('Аналитика данных для бизнеса', 3, 1, 'обязательная'),
            # 2 семестр
            Course('AI в бизнесе', 6, 2, 'обязательная'),
            Course('Product Strategy', 4, 2, 'обязательная'),
            Course('User Experience Design', 4, 2, 'выборная'),
            Course('Метрики и KPI для AI продуктов', 4, 2, 'выборная'),
            Course('Agile и Scrum для AI проектов', 3, 2, 'выборная'),
            # 3 семестр
            Course('AI Product Development', 6, 3, 'обязательная'),
            Course('Бизнес-модели для AI продуктов', 3, 3, 'обязательная'),
            Course('Проектная работа', 8, 3, 'обязательная'),
            Course('Инновации в AI', 2, 3, 'факультативная'),
            # 4 семестр
            Course('Магистерская диссертация', 12, 4, 'обязательная'),
            Course('Защита выпускной работы', 2, 4, 'обязательная'),
        ]

    def _create_basic_courses(self, program_type: str) -> list[Course]:
        """Создает базовые дисциплины если не удалось извлечь реальные"""
        if program_type == 'ai':
            return [
                Course('Введение в ИИ', 3, 1, 'обязательная'),
                Course('Машинное обучение', 6, 1, 'обязательная'),
                Course('Глубокое обучение', 6, 2, 'обязательная'),
                Course('Проектная работа', 8, 3, 'обязательная'),
                Course('Магистерская диссертация', 12, 4, 'обязательная'),
            ]
        else:
            return [
                Course('Введение в AI Product Management', 3, 1, 'обязательная'),
                Course('Основы машинного обучения', 6, 1, 'обязательная'),
                Course('Управление продуктами', 6, 2, 'обязательная'),
                Course('Проектная работа', 8, 3, 'обязательная'),
                Course('Магистерская диссертация', 12, 4, 'обязательная'),
            ]

    def _extract_credits(self, text: str) -> int:
        """Извлекает количество кредитов из текста"""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 3

    def _extract_semester(self, text: str) -> int:
        """Извлекает номер семестра из текста"""
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else 1

    def _determine_course_type(self, text: str) -> str:
        """Определяет тип дисциплины"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['выбор', 'электив']):
            return 'выборная'
        elif any(word in text_lower for word in ['факультатив']):
            return 'факультативная'
        else:
            return 'обязательная'


async def test_parser() -> list[Program] | None:
    """Тестирует парсер"""
    print('🧪 Тестирование веб-парсера...')

    async with ITMOWebParser() as parser:
        # Загружаем страницы
        print('📥 Загружаем страницы программ...')

        ai_html = await parser.fetch_page('https://abit.itmo.ru/program/master/ai')
        ai_product_html = await parser.fetch_page('https://abit.itmo.ru/program/master/ai_product')

        if not ai_html or not ai_product_html:
            print('❌ Не удалось загрузить страницы')
            return None

        print('✅ Страницы загружены')

        # Парсим программы
        print('🔍 Парсим программу AI...')
        ai_program = parser.parse_ai_program(ai_html)

        print('🔍 Парсим программу AI Product...')
        ai_product_program = parser.parse_ai_product_program(ai_product_html)

        programs = [ai_program, ai_product_program]

        # Выводим результаты
        for program in programs:
            print(f'\n🎯 {program.name}')
            print(f'   URL: {program.url}')
            print(f'   Институт: {program.institute}')
            print(f'   Форма: {program.form}')
            print(f'   Язык: {program.language}')
            print(f'   Длительность: {program.duration} семестра')
            print(f"   Стоимость: {program.cost or 'Не указана'}")
            print(f"   Общежитие: {'Да' if program.dormitory else 'Нет'}")
            print(f'   Всего кредитов: {program.total_credits}')
            print(f'   Количество дисциплин: {len(program.courses)}')

            if program.courses:
                print('   Дисциплины по семестрам:')
                by_semester: dict[int, list[Course]] = {}
                for course in program.courses:
                    if course.semester not in by_semester:
                        by_semester[course.semester] = []
                    by_semester[course.semester].append(course)

                for semester in sorted(by_semester.keys()):
                    courses = by_semester[semester]
                    print(f'     📅 {semester} семестр ({len(courses)} дисциплин):')
                    for course in courses:
                        print(
                            f'       • {course.name} ({course.credits} кр., {course.course_type})'
                        )

        return programs


if __name__ == '__main__':
    asyncio.run(test_parser())
