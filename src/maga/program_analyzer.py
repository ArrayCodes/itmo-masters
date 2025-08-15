"""
Интеллектуальный анализатор программ магистратуры с системой рекомендаций
"""

from dataclasses import dataclass

from web_parser import Course, Program


@dataclass
class Recommendation:
    """Рекомендация по дисциплине"""

    course: Course
    score: float
    reason: str
    priority: str  # high, medium, low
    compatibility_score: float  # совместимость с текущими навыками
    learning_path: str  # рекомендуемый путь изучения


@dataclass
class BackgroundProfile:
    """Расширенный профиль бэкграунда абитуриента"""

    programming_skills: list[str]
    math_skills: list[str]
    business_skills: list[str]
    research_interests: list[str]
    work_experience: str
    education_level: str
    career_goals: list[str]
    learning_preferences: list[str]
    time_availability: str


@dataclass
class CourseCluster:
    """Кластер связанных дисциплин"""

    name: str
    courses: list[Course]
    difficulty_level: str  # beginner, intermediate, advanced
    prerequisites: list[str]
    career_relevance: list[str]


class ProgramAnalyzer:
    """Интеллектуальный анализатор программ для персонализированных рекомендаций"""

    # Константы для магических чисел
    MIN_TOKEN_LENGTH = 10
    MAX_MESSAGE_LENGTH = 4096
    MAX_COURSES_DISPLAY = 10
    HIGH_SCORE_THRESHOLD = 7.0
    MEDIUM_SCORE_THRESHOLD = 4.0
    LOW_SCORE_THRESHOLD = 2.0
    FIRST_SEMESTER = 1
    SECOND_SEMESTER = 2
    THIRD_SEMESTER = 3
    FOURTH_SEMESTER = 4

    def __init__(self, programs: list[Program]) -> None:
        self.programs = programs
        self._build_course_index()
        self._build_course_clusters()
        self._build_skill_mapping()

    def _build_course_index(self) -> None:
        """Строит индекс курсов для быстрого поиска"""
        self.course_index: dict[str, list[tuple[Course, Program]]] = {}
        for program in self.programs:
            for course in program.courses:
                key = course.name.lower()
                if key not in self.course_index:
                    self.course_index[key] = []
                self.course_index[key].append((course, program))

    def _build_course_clusters(self) -> None:
        """Строит кластеры связанных дисциплин"""
        self.course_clusters = {
            'ai_core': CourseCluster(
                name='Основы искусственного интеллекта',
                courses=[],
                difficulty_level='intermediate',
                prerequisites=['программирование', 'математика'],
                career_relevance=['ML Engineer', 'AI Developer', 'Data Scientist'],
            ),
            'machine_learning': CourseCluster(
                name='Машинное обучение',
                courses=[],
                difficulty_level='advanced',
                prerequisites=['ai_core', 'статистика', 'линейная алгебра'],
                career_relevance=['ML Engineer', 'Data Scientist', 'AI Researcher'],
            ),
            'deep_learning': CourseCluster(
                name='Глубокое обучение',
                courses=[],
                difficulty_level='advanced',
                prerequisites=['machine_learning', 'нейронные сети'],
                career_relevance=['ML Engineer', 'AI Researcher', 'Computer Vision Engineer'],
            ),
            'nlp': CourseCluster(
                name='Обработка естественного языка',
                courses=[],
                difficulty_level='advanced',
                prerequisites=['machine_learning', 'лингвистика'],
                career_relevance=['NLP Engineer', 'AI Developer', 'Data Scientist'],
            ),
            'computer_vision': CourseCluster(
                name='Компьютерное зрение',
                courses=[],
                difficulty_level='advanced',
                prerequisites=['machine_learning', 'линейная алгебра'],
                career_relevance=['Computer Vision Engineer', 'AI Developer', 'ML Engineer'],
            ),
            'business_ai': CourseCluster(
                name='AI в бизнесе',
                courses=[],
                difficulty_level='intermediate',
                prerequisites=['ai_core', 'бизнес-аналитика'],
                career_relevance=['AI Product Manager', 'Business Analyst', 'Product Manager'],
            ),
            'product_management': CourseCluster(
                name='Управление продуктами',
                courses=[],
                difficulty_level='intermediate',
                prerequisites=['бизнес-аналитика', 'менеджмент'],
                career_relevance=['Product Manager', 'AI Product Manager', 'Business Analyst'],
            ),
            'data_analytics': CourseCluster(
                name='Анализ данных',
                courses=[],
                difficulty_level='intermediate',
                prerequisites=['статистика', 'программирование'],
                career_relevance=['Data Analyst', 'Business Analyst', 'Data Scientist'],
            ),
        }

        # Распределяем курсы по кластерам
        for program in self.programs:
            for course in program.courses:
                self._assign_course_to_cluster(course)

    def _assign_course_to_cluster(self, course: Course):
        """Назначает курс в соответствующий кластер"""
        course_lower = course.name.lower()

        # Определяем кластер на основе названия и типа курса
        if any(keyword in course_lower for keyword in ['введение', 'основы', 'базовые']):
            if 'искусственный интеллект' in course_lower or 'ai' in course_lower:
                self.course_clusters['ai_core'].courses.append(course)
            elif 'продукт' in course_lower or 'менеджмент' in course_lower:
                self.course_clusters['product_management'].courses.append(course)
            elif 'анализ' in course_lower or 'данные' in course_lower:
                self.course_clusters['data_analytics'].courses.append(course)

        elif any(
            keyword in course_lower for keyword in ['машинное обучение', 'ml', 'machine learning']
        ):
            self.course_clusters['machine_learning'].courses.append(course)

        elif any(
            keyword in course_lower
            for keyword in ['глубокое обучение', 'deep learning', 'нейронные сети']
        ):
            self.course_clusters['deep_learning'].courses.append(course)

        elif any(keyword in course_lower for keyword in ['естественный язык', 'nlp', 'текст']):
            self.course_clusters['nlp'].courses.append(course)

        elif any(keyword in course_lower for keyword in ['зрение', 'vision', 'изображения']):
            self.course_clusters['computer_vision'].courses.append(course)

        elif any(
            keyword in course_lower for keyword in ['бизнес', 'предпринимательство', 'стратегия']
        ):
            if 'ai' in course_lower or 'искусственный интеллект' in course_lower:
                self.course_clusters['business_ai'].courses.append(course)
            else:
                self.course_clusters['product_management'].courses.append(course)

        elif any(keyword in course_lower for keyword in ['анализ', 'данные', 'статистика']):
            self.course_clusters['data_analytics'].courses.append(course)

    def _build_skill_mapping(self) -> None:
        """Строит карту соответствия навыков и курсов"""
        self.skill_mapping = {
            'python': {
                'courses': ['программирование', 'python', 'код', 'разработка'],
                'weight': 2.0,
                'career_paths': ['ML Engineer', 'Data Scientist', 'AI Developer'],
            },
            'java': {
                'courses': ['java', 'джава', 'программирование', 'код'],
                'weight': 1.5,
                'career_paths': ['Software Engineer', 'Backend Developer'],
            },
            'javascript': {
                'courses': ['javascript', 'js', 'веб', 'web', 'frontend'],
                'weight': 1.5,
                'career_paths': ['Frontend Developer', 'Full-Stack Developer'],
            },
            'mathematics': {
                'courses': ['математика', 'алгебра', 'геометрия', 'анализ'],
                'weight': 2.0,
                'career_paths': ['ML Engineer', 'Data Scientist', 'AI Researcher'],
            },
            'statistics': {
                'courses': ['статистика', 'вероятность', 'анализ данных'],
                'weight': 2.5,
                'career_paths': ['Data Scientist', 'Data Analyst', 'ML Engineer'],
            },
            'linear_algebra': {
                'courses': ['линейная алгебра', 'матрицы', 'векторы'],
                'weight': 2.0,
                'career_paths': ['ML Engineer', 'Computer Vision Engineer', 'AI Researcher'],
            },
            'business': {
                'courses': ['бизнес', 'менеджмент', 'управление', 'стратегия'],
                'weight': 1.5,
                'career_paths': ['Product Manager', 'AI Product Manager', 'Business Analyst'],
            },
            'product_management': {
                'courses': ['продукт', 'product', 'управление продуктами'],
                'weight': 2.0,
                'career_paths': ['Product Manager', 'AI Product Manager'],
            },
            'research': {
                'courses': ['исследование', 'наука', 'анализ', 'публикация'],
                'weight': 1.5,
                'career_paths': ['AI Researcher', 'Data Scientist', 'ML Engineer'],
            },
            'general': {
                'courses': [
                    'техническое',
                    'технический',
                    'инженер',
                    'инженерный',
                    'разработка',
                    'разработчик',
                    'программирование',
                    'код',
                ],
                'weight': 1.5,
                'career_paths': ['Software Engineer', 'ML Engineer', 'AI Developer'],
            },
            'c++': {
                'courses': ['c++', 'cpp', 'си плюс плюс', 'программирование', 'код', 'разработка'],
                'weight': 1.5,
                'career_paths': ['Software Engineer', 'Backend Developer', 'ML Engineer'],
            },
            'web': {
                'courses': ['веб', 'web', 'html', 'css', 'frontend', 'backend', 'fullstack'],
                'weight': 1.5,
                'career_paths': ['Frontend Developer', 'Full-Stack Developer', 'Web Developer'],
            },
            'mobile': {
                'courses': ['мобильная разработка', 'android', 'ios', 'react native', 'flutter'],
                'weight': 1.5,
                'career_paths': ['Mobile Developer', 'App Developer'],
            },
            'blockchain': {
                'courses': ['блокчейн', 'blockchain', 'криптовалюта', 'смарт-контракт', 'defi'],
                'weight': 1.5,
                'career_paths': ['Blockchain Developer', 'Smart Contract Developer'],
            },
            'ai': {
                'courses': [
                    'искусственный интеллект',
                    'ai',
                    'машинное обучение',
                    'нейронные сети',
                    'data science',
                ],
                'weight': 2.0,
                'career_paths': ['ML Engineer', 'AI Developer', 'Data Scientist'],
            },
            'data': {
                'courses': ['данные', 'data', 'анализ данных', 'big data', 'база данных'],
                'weight': 2.0,
                'career_paths': ['Data Scientist', 'Data Engineer', 'Data Analyst'],
            },
            'devops': {
                'courses': ['devops', 'инфраструктура', 'docker', 'kubernetes', 'ci/cd'],
                'weight': 1.5,
                'career_paths': ['DevOps Engineer', 'Infrastructure Engineer'],
            },
        }

    def get_program_comparison(self) -> str:
        """Возвращает детальное сравнение программ"""
        comparison = '📊 Сравнение магистерских программ:\n\n'

        for program in self.programs:
            comparison += f'🎯 {program.name}\n'
            comparison += f'🏛️  Институт: {program.institute}\n'
            comparison += f'📚 Всего дисциплин: {len(program.courses)}\n'
            comparison += f'🎓 Общее количество кредитов: {program.total_credits}\n'
            comparison += f'⏱ Длительность: {program.duration} семестра\n'
            comparison += f'📖 Форма обучения: {program.form}\n'
            comparison += f'🌍 Язык обучения: {program.language}\n'

            if program.cost:
                comparison += f'💰 Стоимость: {program.cost}\n'

            comparison += f"🏠 Общежитие: {'Да' if program.dormitory else 'Нет'}\n"
            comparison += (
                f"🎖️  Военный учебный центр: {'Да' if program.military_center else 'Нет'}\n"
            )
            comparison += f"✅ Гос. аккредитация: {'Да' if program.accreditation else 'Нет'}\n\n"

        return comparison

    def get_detailed_program_info(self, program_name: str) -> str:
        """Возвращает детальную информацию о конкретной программе"""
        program = self._find_program_by_name(program_name)
        if not program:
            return '❌ Программа не найдена'

        info = f'🎯 {program.name}\n'
        info += f'🏛️  Институт: {program.institute}\n'
        info += f'📖 Описание: {program.description[:200]}...\n\n'

        # Группируем дисциплины по семестрам
        by_semester = {}
        for course in program.courses:
            if course.semester not in by_semester:
                by_semester[course.semester] = []
            by_semester[course.semester].append(course)

        for semester in sorted(by_semester.keys()):
            courses = by_semester[semester]
            info += f'📅 {semester} семестр ({len(courses)} дисциплин):\n'

            # Группируем по типам
            by_type = {}
            for course in courses:
                if course.course_type not in by_type:
                    by_type[course.course_type] = []
                by_type[course.course_type].append(course)

            for course_type, type_courses in by_type.items():
                info += f'   📖 {course_type.title()}:\n'
                for course in type_courses:
                    info += f'      • {course.name} ({course.credits} кредитов)\n'

            info += '\n'

        return info

    def get_course_recommendations(self, background: str) -> str:
        """Генерирует краткие и конкретные рекомендации по дисциплинам"""
        profile = self._analyze_background(background)

        # Определяем основной профиль пользователя
        if profile.programming_skills:
            if 'python' in profile.programming_skills:
                user_type = 'python_dev'
            elif 'java' in profile.programming_skills:
                user_type = 'java_dev'
            else:
                user_type = 'tech_dev'
        elif profile.math_skills:
            user_type = 'math_background'
        elif profile.business_skills:
            user_type = 'business_background'
        else:
            user_type = 'beginner'

        recommendations = '💡 Рекомендации по дисциплинам:\n\n'

        # Анализируем профиль и даем дифференцированные рекомендации
        ai_score = 0
        product_score = 0

        # Оцениваем подходящесть для AI программы
        if user_type == 'python_dev':
            ai_score += 3  # Python идеален для ML
            product_score += 1  # Хорошо, но не идеально
        elif user_type == 'java_dev':
            ai_score += 2  # Java подходит для enterprise AI
            product_score += 1
        elif user_type == 'tech_dev':
            ai_score += 2  # Технический бэкграунд важен для AI
            product_score += 2  # И для продуктов тоже
        elif user_type == 'math_background':
            ai_score += 3  # Математика критична для ML
            product_score += 0  # Не очень важно для продуктов
        elif user_type == 'business_background':
            ai_score += 0  # Бизнес-навыки не критичны для AI
            product_score += 3  # Идеально для продуктов
        else:
            ai_score += 1
            product_score += 1

        # Даем дифференцированные рекомендации для каждой программы
        for program in self.programs:
            program_name = program.name.lower()

            if 'искусственный интеллект' in program_name or (
                'ai' in program_name and 'product' not in program_name
            ):
                if user_type == 'python_dev':
                    recommendations += (
                        f'🎯 {program.name}: 🔥 ЛУЧШИЙ ВЫБОР! Python + ML = идеальная комбинация\n'
                    )
                elif user_type == 'java_dev':
                    recommendations += (
                        f'🎯 {program.name}: ⭐ Хорошо подходит! Enterprise AI с Java\n'
                    )
                elif user_type == 'tech_dev':
                    recommendations += (
                        f'🎯 {program.name}: ⭐ Хорошо подходит! Ваши навыки программирования\n'
                    )
                elif user_type == 'math_background':
                    recommendations += (
                        f'🎯 {program.name}: 🔥 ЛУЧШИЙ ВЫБОР! Математика = основа ML\n'
                    )
                elif user_type == 'business_background':
                    recommendations += f'🎯 {program.name}: 💡 Можно рассмотреть, но не идеально\n'
                else:
                    recommendations += f'🎯 {program.name}: 💡 Хороший выбор для начала\n'

            elif 'продукт' in program_name or 'product' in program_name:
                if user_type == 'business_background':
                    recommendations += (
                        f'🎯 {program.name}: 🔥 ЛУЧШИЙ ВЫБОР! Бизнес + AI = идеально\n'
                    )
                elif user_type == 'tech_dev':
                    recommendations += f'🎯 {program.name}: ⭐ Хорошо подходит! Техника + бизнес\n'
                elif user_type in ('python_dev', 'java_dev'):
                    recommendations += (
                        f'🎯 {program.name}: ⭐ Хорошо подходит! Программирование + продукт\n'
                    )
                elif user_type == 'math_background':
                    recommendations += f'🎯 {program.name}: 💡 Можно рассмотреть, но не идеально\n'
                else:
                    recommendations += f'🎯 {program.name}: 💡 Хороший выбор для начала\n'

        return recommendations

    def _analyze_background(self, background: str) -> BackgroundProfile:
        """Анализирует бэкграунд абитуриента"""
        background_lower = background.lower()

        # Анализируем навыки программирования
        programming_keywords = {
            'python': [
                'python',
                'питон',
                'программирую на python',
                'знаю python',
                'работаю с python',
            ],
            'java': ['java', 'джава', 'программирую на java', 'знаю java', 'работаю с java'],
            'c++': ['c++', 'cpp', 'си плюс плюс', 'программирую на c++', 'знаю c++'],
            'javascript': ['javascript', 'js', 'джаваскрипт', 'программирую на js', 'знаю js'],
            'web': [
                'веб',
                'web',
                'html',
                'css',
                'frontend',
                'backend',
                'fullstack',
                'веб-разработка',
                'делаю сайты',
            ],
            'mobile': [
                'мобильная разработка',
                'android',
                'ios',
                'react native',
                'flutter',
                'мобильные приложения',
                'разрабатываю приложения',
            ],
            'blockchain': ['блокчейн', 'blockchain', 'криптовалюта', 'смарт-контракт', 'defi'],
            'ai': [
                'искусственный интеллект',
                'ai',
                'машинное обучение',
                'нейронные сети',
                'data science',
            ],
            'data': [
                'данные',
                'data',
                'анализ данных',
                'big data',
                'база данных',
                'работаю с данными',
            ],
            'devops': [
                'devops',
                'инфраструктура',
                'docker',
                'kubernetes',
                'ci/cd',
                'развертывание',
            ],
            'general': [
                'техническое',
                'технический',
                'инженер',
                'инженерный',
                'разработка',
                'разработчик',
                'программирование',
                'код',
                'программист',
            ],
        }

        programming_skills = []
        for skill, keywords in programming_keywords.items():
            # Проверяем, что это не отрицание и перед ключевым словом нет отрицания
            if any(keyword in background_lower for keyword in keywords) and not any(
                neg in background_lower
                for neg in ['не знаю', 'не умею', 'не понимаю', 'не владею', 'не программирую']
            ):
                programming_skills.append(skill)

        # Анализируем математические навыки
        math_keywords = {
            'математика': [
                'математика',
                'математический',
                'алгебра',
                'геометрия',
                'анализ',
                'математик',
                'хорошо знаю математику',
                'силен в математике',
                'люблю математику',
            ],
            'статистика': [
                'статистика',
                'статистический',
                'вероятность',
                'математическая статистика',
                'работаю со статистикой',
                'анализирую данные',
            ],
            'линейная алгебра': [
                'линейная алгебра',
                'матрицы',
                'векторы',
                'линейные преобразования',
            ],
            'математический анализ': [
                'математический анализ',
                'дифференциальные уравнения',
                'интегралы',
            ],
            'дискретная математика': ['дискретная математика', 'комбинаторика', 'теория графов'],
            'алгоритмы': ['алгоритм', 'алгоритмы', 'структуры данных', 'сложность', 'оптимизация'],
            'логика': ['логика', 'логический', 'теория множеств', 'математическая логика'],
        }

        math_skills = []
        for skill, keywords in math_keywords.items():
            if any(keyword in background_lower for keyword in keywords):
                math_skills.append(skill)

        # Анализируем бизнес-навыки
        business_keywords = {
            'менеджмент': [
                'менеджмент',
                'управление',
                'бизнес',
                'предпринимательство',
                'менеджер',
                'руковожу',
                'управляю командой',
                'работаю в менеджменте',
            ],
            'маркетинг': [
                'маркетинг',
                'реклама',
                'продвижение',
                'продажи',
                'маркетолог',
                'работаю в маркетинге',
                'занимаюсь продвижением',
            ],
            'экономика': [
                'экономика',
                'экономический',
                'финансы',
                'бухгалтерия',
                'экономист',
                'работаю с финансами',
            ],
            'проектное управление': [
                'проектное управление',
                'agile',
                'scrum',
                'kanban',
                'project manager',
                'управляю проектами',
                'работаю по agile',
            ],
            'продукт': [
                'продукт',
                'product',
                'продуктовая аналитика',
                'product manager',
                'работаю с продуктами',
                'продуктовый менеджер',
            ],
            'стратегия': [
                'стратегия',
                'стратегический',
                'планирование',
                'анализ рынка',
                'стратегическое планирование',
            ],
        }

        business_skills = []
        for skill, keywords in business_keywords.items():
            if any(keyword in background_lower for keyword in keywords):
                business_skills.append(skill)

        # Анализируем исследовательские интересы
        research_keywords = [
            'исследование',
            'наука',
            'публикация',
            'конференция',
            'статья',
            'лаборатория',
        ]
        research_interests = [
            keyword for keyword in research_keywords if keyword in background_lower
        ]

        # Определяем уровень образования
        education_keywords = {
            'бакалавриат': ['бакалавр', 'бакалавриат', 'высшее образование'],
            'магистратура': ['магистр', 'магистратура'],
            'аспирантура': ['аспирант', 'аспирантура', 'кандидат наук'],
            'техническое': [
                'техническое образование',
                'технический',
                'инженерное',
                'инженерный',
                'техническое',
            ],
        }

        education_level = 'бакалавриат'  # по умолчанию
        for level, keywords in education_keywords.items():
            if any(keyword in background_lower for keyword in keywords):
                education_level = level
                break

        # Определяем опыт работы
        work_experience = 'нет опыта'
        if any(
            word in background_lower
            for word in [
                'работаю',
                'работал',
                'опыт работы',
                'стаж',
                'программист',
                'разработчик',
                'инженер',
                'аналитик',
                'менеджер',
                'специалист',
                'опыт в разработке',
                'опыт разработки',
                'опыт',
                'разработка',
                'код',
                'программирование',
            ]
        ):
            work_experience = 'есть опыт'

        # Анализируем карьерные цели
        career_goals = []
        career_keywords = {
            'ML Engineer': ['ml engineer', 'машинное обучение', 'инженер ml', 'ml разработчик'],
            'Data Scientist': ['data scientist', 'ученый по данным', 'аналитик данных'],
            'AI Developer': ['ai developer', 'разработчик ии', 'разработчик ai'],
            'Product Manager': ['product manager', 'продукт менеджер', 'менеджер продукта'],
            'AI Product Manager': ['ai product manager', 'продукт менеджер ai'],
            'Business Analyst': ['business analyst', 'бизнес аналитик', 'аналитик'],
            'AI Researcher': ['ai researcher', 'исследователь ии', 'ученый ии'],
        }

        for goal, keywords in career_keywords.items():
            if any(keyword in background_lower for keyword in keywords):
                career_goals.append(goal)

        # Анализируем предпочтения в обучении
        learning_preferences = []
        if any(
            keyword in background_lower for keyword in ['практика', 'проекты', 'реальные задачи']
        ):
            learning_preferences.append('практико-ориентированное')
        if any(keyword in background_lower for keyword in ['теория', 'наука', 'исследование']):
            learning_preferences.append('теоретическое')
        if any(keyword in background_lower for keyword in ['группа', 'команда', 'совместно']):
            learning_preferences.append('групповое')
        if any(keyword in background_lower for keyword in ['индивидуально', 'самостоятельно']):
            learning_preferences.append('индивидуальное')

        # Определяем доступность времени
        time_availability = 'стандартная'
        if any(keyword in background_lower for keyword in ['полный день', 'очная', 'дневная']):
            time_availability = 'полный день'
        elif any(keyword in background_lower for keyword in ['вечерняя', 'заочная', 'частичная']):
            time_availability = 'частичная'

        profile = BackgroundProfile(
            programming_skills=programming_skills,
            math_skills=math_skills,
            business_skills=business_skills,
            research_interests=research_interests,
            work_experience=work_experience,
            education_level=education_level,
            career_goals=career_goals,
            learning_preferences=learning_preferences,
            time_availability=time_availability,
        )

        return profile

    def _evaluate_course_intelligently(
        self, course: Course, profile: BackgroundProfile, program: Program
    ) -> Recommendation:
        """Интеллектуально оценивает релевантность курса"""
        score = 0.0
        reasons = []
        compatibility_score = 0.0

        course_lower = course.name.lower()

        # Оцениваем по навыкам программирования
        if profile.programming_skills:
            for skill in profile.programming_skills:
                # Проверяем по карте навыков
                if skill in self.skill_mapping:
                    skill_info = self.skill_mapping[skill]
                    if any(keyword in course_lower for keyword in skill_info['courses']):
                        score += skill_info['weight']
                        compatibility_score += skill_info['weight']
                        reasons.append(f'Соответствует вашим навыкам в {skill}')
                        break

                # Проверяем по ключевым словам курса
                if any(
                    keyword in course_lower
                    for keyword in [
                        'программирование',
                        'код',
                        'разработка',
                        'алгоритм',
                        'python',
                        'java',
                        'javascript',
                        'ai',
                        'data',
                        'blockchain',
                        'машинное обучение',
                        'глубокое обучение',
                        'нейронные сети',
                        'обработка',
                        'зрение',
                        'анализ',
                    ]
                ):
                    score += 2.0
                    compatibility_score += 2.0
                    reasons.append(f'Соответствует вашим навыкам в {skill}')
                    break

        # Оцениваем по математическим навыкам
        if profile.math_skills:
            for skill in profile.math_skills:
                # Проверяем по карте навыков
                if skill in self.skill_mapping:
                    skill_info = self.skill_mapping[skill]
                    if any(keyword in course_lower for keyword in skill_info['courses']):
                        score += skill_info['weight']
                        compatibility_score += skill_info['weight']
                        reasons.append(f'Соответствует вашим навыкам в {skill}')
                        break

                # Проверяем по ключевым словам курса
                if any(
                    keyword in course_lower
                    for keyword in [
                        'математика',
                        'статистика',
                        'анализ',
                        'алгоритм',
                        'алгебра',
                        'геометрия',
                        'машинное обучение',
                        'глубокое обучение',
                        'нейронные сети',
                        'обработка',
                        'зрение',
                        'вероятности',
                    ]
                ):
                    score += 2.0
                    compatibility_score += 2.0
                    reasons.append(f'Соответствует вашим навыкам в {skill}')
                    break

        # Оцениваем по бизнес-навыкам
        if profile.business_skills:
            for skill in profile.business_skills:
                # Проверяем по карте навыков
                if skill in self.skill_mapping:
                    skill_info = self.skill_mapping[skill]
                    if any(keyword in course_lower for keyword in skill_info['courses']):
                        score += skill_info['weight']
                        compatibility_score += skill_info['weight']
                        reasons.append(f'Соответствует вашим навыкам в {skill}')
                        break

                # Проверяем по ключевым словам курса
                if any(
                    keyword in course_lower
                    for keyword in [
                        'менеджмент',
                        'бизнес',
                        'продукт',
                        'проект',
                        'управление',
                        'стратегия',
                    ]
                ):
                    score += 2.0
                    compatibility_score += 2.0
                    reasons.append(f'Соответствует вашим навыкам в {skill}')
                    break

        # Оцениваем по карьерным целям
        if profile.career_goals:
            for goal in profile.career_goals:
                for _skill_name, skill_info in self.skill_mapping.items():
                    if goal.lower() in skill_info['career_paths'] and any(
                        keyword in course_lower for keyword in skill_info['courses']
                    ):
                        score += 1.5
                        reasons.append(f'Соответствует вашей карьерной цели: {goal}')
                        break

        # Оцениваем по исследовательским интересам
        if profile.research_interests and any(
            skill in course_lower for skill in ['исследование', 'наука', 'анализ']
        ):
            score += 1.5
            reasons.append('Соответствует вашим исследовательским интересам')

        # Бонус за опыт работы
        if profile.work_experience == 'есть опыт' and any(
            skill in course_lower for skill in ['практика', 'проект', 'реальный']
        ):
            score += 1.0
            reasons.append('Подходит для специалистов с опытом работы')

        # Бонус за продвинутый уровень образования
        if profile.education_level in ['магистратура', 'аспирантура'] and any(
            skill in course_lower for skill in ['продвинутый', 'углубленный', 'исследование']
        ):
            score += 1.0
            reasons.append('Подходит для вашего уровня образования')

        # Оцениваем сложность курса
        difficulty_bonus = self._assess_course_difficulty(course, profile)
        score += difficulty_bonus

        # Определяем приоритет
        if score >= self.HIGH_SCORE_THRESHOLD:
            priority = 'high'
        elif score >= self.MEDIUM_SCORE_THRESHOLD:
            priority = 'medium'
        else:
            priority = 'low'

        # Базовая оценка для всех курсов
        if score == 0.0:
            score = 1.0
            reasons.append('Базовый курс для всех студентов')

        # Формируем конкретную причину рекомендации
        reason = self._generate_concrete_recommendation_reason(course, profile, score)

        # Определяем рекомендуемый путь изучения
        learning_path = self._determine_learning_path(course, profile, program)

        return Recommendation(
            course=course,
            score=min(score, 10.0),
            reason=reason,
            priority=priority,
            compatibility_score=min(compatibility_score, 10.0),
            learning_path=learning_path,
        )

    def _assess_course_difficulty(self, course: Course, profile: BackgroundProfile) -> float:
        """Оценивает сложность курса для профиля"""
        difficulty_score = 0.0
        course_lower = course.name.lower()

        # Определяем базовую сложность курса
        if any(keyword in course_lower for keyword in ['введение', 'основы', 'базовые']):
            base_difficulty = 1.0
        elif any(
            keyword in course_lower for keyword in ['продвинутый', 'углубленный', 'специальные']
        ):
            base_difficulty = 3.0
        else:
            base_difficulty = 2.0

        # Корректируем сложность на основе навыков
        if profile.programming_skills and any(
            keyword in course_lower for keyword in ['программирование', 'код', 'разработка']
        ):
            difficulty_score -= 1.0  # Упрощаем для программистов

        if profile.math_skills and any(
            keyword in course_lower for keyword in ['математика', 'алгебра', 'статистика']
        ):
            difficulty_score -= 1.0  # Упрощаем для математиков

        if profile.business_skills and any(
            keyword in course_lower for keyword in ['бизнес', 'менеджмент', 'управление']
        ):
            difficulty_score -= 1.0  # Упрощаем для бизнесменов

        return base_difficulty + difficulty_score

    def _determine_learning_path(
        self, course: Course, profile: BackgroundProfile, program: Program
    ) -> str:
        """Определяет рекомендуемый путь изучения"""

        # Определяем последовательность изучения
        if course.semester == self.FIRST_SEMESTER:
            return 'Рекомендуется изучать в первую очередь (1 семестр)'
        elif course.semester == self.SECOND_SEMESTER:
            return 'Изучать после освоения базовых дисциплин (2 семестр)'
        elif course.semester == self.THIRD_SEMESTER:
            return 'Изучать после освоения основных дисциплин (3 семестр)'
        elif course.semester == self.FOURTH_SEMESTER:
            return 'Изучать в завершающем семестре (4 семестр)'

        return 'Можно изучать в любом порядке'

    def _get_program_recommendations(
        self, program: Program, profile: BackgroundProfile
    ) -> list[Recommendation]:
        """Получает рекомендации для конкретной программы"""
        recommendations = []

        # Получаем выборные и факультативные дисциплины
        elective_courses = [
            c for c in program.courses if c.course_type in ['выборная', 'факультативная']
        ]

        if not elective_courses:
            # Если нет выборных, берем все дисциплины кроме обязательных
            elective_courses = [c for c in program.courses if c.course_type != 'обязательная']

        # Если все еще нет, берем все дисциплины
        if not elective_courses:
            elective_courses = program.courses

        # Оцениваем каждый курс
        for course in elective_courses:
            recommendation = self._evaluate_course_intelligently(course, profile, program)
            if recommendation.score > 0:
                recommendations.append(recommendation)

        # Сортируем по релевантности
        recommendations.sort(key=lambda x: x.score, reverse=True)

        return recommendations

    def _get_cluster_recommendations(self, program: Program, profile: BackgroundProfile) -> str:
        """Получает рекомендации по кластерам дисциплин"""
        recommendations = ''

        # Анализируем профиль и рекомендуем кластеры
        if profile.programming_skills and profile.math_skills:
            if 'ai_core' in self.course_clusters and self.course_clusters['ai_core'].courses:
                recommendations += '      🧠 Основы ИИ - отличный старт для программистов\n'

            if (
                'machine_learning' in self.course_clusters
                and self.course_clusters['machine_learning'].courses
            ):
                recommendations += '      🤖 Машинное обучение - ключевое направление\n'

        if profile.business_skills:
            if (
                'business_ai' in self.course_clusters
                and self.course_clusters['business_ai'].courses
            ):
                recommendations += '      💼 AI в бизнесе - примените ИИ на практике\n'

            if (
                'product_management' in self.course_clusters
                and self.course_clusters['product_management'].courses
            ):
                recommendations += '      📊 Управление продуктами - развивайте бизнес-навыки\n'

        if (
            profile.research_interests
            and 'deep_learning' in self.course_clusters
            and self.course_clusters['deep_learning'].courses
        ):
            recommendations += '      🔬 Глубокое обучение - для исследователей\n'

        if not recommendations:
            recommendations = (
                '      📚 Рекомендуем изучать дисциплины последовательно по семестрам\n'
            )

        return recommendations

    def _generate_concrete_recommendation_reason(
        self, course: Course, profile: BackgroundProfile, compatibility_score: float
    ) -> str:
        """Генерирует конкретную причину рекомендации"""
        course_lower = course.name.lower()

        # Конкретные советы для программистов
        if profile.programming_skills:
            if 'python' in profile.programming_skills and (
                'машинное обучение' in course_lower or 'нейронные сети' in course_lower
            ):
                return 'Отличный выбор для Python-разработчиков! Этот курс даст вам практические навыки в ML'
            elif 'python' in profile.programming_skills and (
                'обработка' in course_lower or 'зрение' in course_lower
            ):
                return 'Идеально подходит для Python-программистов. Вы сможете применить свои навыки в AI'
            elif 'python' in profile.programming_skills and 'алгоритм' in course_lower:
                return 'Ваш опыт в Python поможет быстро освоить алгоритмы и структуры данных'

            if 'java' in profile.programming_skills and 'машинное обучение' in course_lower:
                return 'Отличный выбор! Java отлично подходит для enterprise ML-решений'
            elif 'java' in profile.programming_skills and 'алгоритм' in course_lower:
                return 'Ваши навыки в Java помогут эффективно реализовать алгоритмы'

        # Конкретные советы для математиков
        if (
            profile.math_skills
            and 'математика' in profile.math_skills
            and ('машинное обучение' in course_lower or 'нейронные сети' in course_lower)
        ):
            return 'Ваша математическая база идеальна для понимания ML-алгоритмов'
        elif (
            profile.math_skills
            and 'математика' in profile.math_skills
            and 'статистика' in course_lower
        ):
            return 'Математическое образование поможет глубоко понять статистические методы'
        elif (
            profile.math_skills
            and 'математика' in profile.math_skills
            and 'оптимизация' in course_lower
        ):
            return 'Математические навыки дадут вам преимущество в изучении оптимизации'

        # Конкретные советы для бизнес-специалистов
        if (
            profile.business_skills
            and 'менеджмент' in profile.business_skills
            and ('продукт' in course_lower or 'проект' in course_lower)
        ):
            return 'Отличный выбор для менеджеров! Курс поможет управлять AI-проектами'
        elif (
            profile.business_skills
            and 'менеджмент' in profile.business_skills
            and 'бизнес' in course_lower
        ):
            return 'Ваш бизнес-опыт поможет понять, как применять AI в реальных проектах'

        # Конкретные советы по карьерным целям
        if profile.career_goals:
            for goal in profile.career_goals:
                if ('ml engineer' in goal.lower() or 'ai developer' in goal.lower()) and (
                    'машинное обучение' in course_lower or 'нейронные сети' in course_lower
                ):
                    return 'Обязательный курс для ML Engineer! Даст ключевые навыки для карьеры'
                elif (
                    'ml engineer' in goal.lower() or 'ai developer' in goal.lower()
                ) and 'алгоритм' in course_lower:
                    return 'Важно для ML Engineer: понимание алгоритмов критично для разработки моделей'

                elif 'data scientist' in goal.lower() and (
                    'статистика' in course_lower or 'анализ' in course_lower
                ):
                    return 'Ключевой курс для Data Scientist! Статистика - основа анализа данных'
                elif 'data scientist' in goal.lower() and 'машинное обучение' in course_lower:
                    return 'Обязательно для Data Scientist! ML - основной инструмент в работе'

                elif 'product manager' in goal.lower() and (
                    'продукт' in course_lower or 'менеджмент' in course_lower
                ):
                    return 'Идеально для Product Manager! Поможет управлять AI-продуктами'
                elif 'product manager' in goal.lower() and 'бизнес' in course_lower:
                    return 'Важно для PM: понимание бизнес-аспектов AI-проектов'

        # Конкретные советы по опыту работы
        if profile.work_experience == 'есть опыт' and (
            'практика' in course_lower or 'проект' in course_lower
        ):
            return 'Ваш опыт работы поможет успешно выполнять практические задания'
        elif profile.work_experience == 'есть опыт' and 'реальный' in course_lower:
            return 'Опыт работы даст вам преимущество в понимании реальных применений'

        # Конкретные советы по уровню образования
        if profile.education_level == 'магистратура' and (
            'продвинутый' in course_lower or 'углубленный' in course_lower
        ):
            return 'Подходит для вашего уровня! Магистратура даст вам базу для сложных курсов'

        # Если ничего не подошло, даем персонализированный совет
        if compatibility_score >= self.MEDIUM_SCORE_THRESHOLD:
            if profile.programming_skills:
                return f'Отличный выбор для {profile.programming_skills[0]}-разработчика! Курс идеально подходит вашему профилю'
            elif profile.math_skills:
                return f'Отличный выбор! Ваши знания в {profile.math_skills[0]} помогут быстро освоить материал'
            else:
                return 'Отличный выбор! Курс хорошо соответствует вашему профилю'
        elif compatibility_score >= self.LOW_SCORE_THRESHOLD:
            if profile.work_experience == 'есть опыт':
                return 'Хороший выбор для расширения кругозора. Ваш опыт работы поможет в освоении'
            else:
                return 'Хороший выбор для развития новых навыков. Рекомендуем дополнительную подготовку'
        else:
            return (
                'Курс может быть сложным для вашего профиля, но это отличная возможность для роста!'
            )

    def _format_recommendation(self, recommendation: Recommendation, priority: str) -> str:
        """Форматирует рекомендацию для вывода"""
        priority_emoji = {'high': '🔥', 'medium': '⭐', 'low': '💡'}

        formatted = f'      {priority_emoji[priority]} {recommendation.course.name}\n'
        formatted += f'         💭 {recommendation.reason}\n\n'

        return formatted

    def _find_program_by_name(self, program_name: str) -> Program | None:
        """Находит программу по названию"""
        program_name_lower = program_name.lower()
        for program in self.programs:
            if program_name_lower in program.name.lower():
                return program
        return None

    def get_program_by_keywords(self, keywords: str) -> list[Program]:
        """Находит программы по ключевым словам"""
        keywords_lower = keywords.lower()
        matching_programs = []

        for program in self.programs:
            # Проверяем название программы
            if keywords_lower in program.name.lower():
                matching_programs.append(program)
                continue

            # Проверяем описание
            if keywords_lower in program.description.lower():
                matching_programs.append(program)
                continue

            # Проверяем дисциплины
            for course in program.courses:
                if keywords_lower in course.name.lower():
                    matching_programs.append(program)
                    break

        return matching_programs

    def get_career_paths(self, program_name: str) -> str:
        """Возвращает информацию о карьерных путях"""
        program = self._find_program_by_name(program_name)
        if not program:
            return '❌ Программа не найдена'

        if 'искусственный интеллект' in program.name.lower():
            career_info = """
🎯 Карьерные пути для программы "Искусственный интеллект":

💼 ML Engineer (Middle уровень):
   • Создает и внедряет ML-модели в продакшен
   • Зарплата: 170,000 - 300,000 рублей
   • Компании: Яндекс, Сбер, МТС, Ozon

💼 Data Engineer:
   • Выстраивает процессы сбора, хранения и обработки данных
   • Зарплата: 150,000 - 280,000 рублей
   • Компании: X5 Group, Норникель, Napoleon IT

💼 AI Product Developer:
   • Разрабатывает продукты на основе AI
   • Зарплата: 180,000 - 320,000 рублей
   • Компании: Genotek, Raft, AIRI

💼 Data Analyst:
   • Анализирует массивы данных и помогает бизнесу принимать решения
   • Зарплата: 120,000 - 250,000 рублей
   • Компании: Wildberries, Huawei, Tinkoff Bank
"""
        elif 'product' in program.name.lower():
            career_info = """
🎯 Карьерные пути для программы "AI Product Management":

💼 Product Manager:
   • Управляет разработкой AI-продуктов
   • Зарплата: 200,000 - 400,000 рублей
   • Компании: Яндекс, Сбер, МТС

💼 AI Product Owner:
   • Определяет требования к AI-продуктам
   • Зарплата: 180,000 - 350,000 рублей
   • Компании: Ozon, X5 Group, Норникель

💼 Business Analyst:
   • Анализирует бизнес-процессы и данные
   • Зарплата: 150,000 - 300,000 рублей
   • Компании: Napoleon IT, Genotek, Raft

💼 Innovation Manager:
   • Управляет инновационными проектами в сфере AI
   • Зарплата: 160,000 - 320,000 рублей
   • Компании: AIRI, DeepPavlov, Just AI
"""
        else:
            career_info = '❌ Информация о карьерных путях недоступна для данной программы'

        return career_info

    def get_admission_info(self, program_name: str) -> str:
        """Возвращает информацию о поступлении"""
        program = self._find_program_by_name(program_name)
        if not program:
            return '❌ Программа не найдена'

        admission_info = f"""
🎓 Информация о поступлении на программу "{program.name}":

📋 Способы поступления:

1️⃣ Вступительный экзамен:
   • Дистанционный формат
   • 100-балльная шкала
   • Необходимо подать документы через личный кабинет

2️⃣ Junior ML Contest:
   • Конкурс проектов с применением ML
   • Курс "My First Data Project"
   • Поступление без экзаменов

3️⃣ Олимпиада "Я-профессионал":
   • Медалисты и победители поступают без экзаменов
   • Действует в год победы и следующий год

4️⃣ Конкурс "Портфолио":
   • Научные достижения и публикации
   • Нужно набрать более 85 баллов

5️⃣ МегаОлимпиада ИТМО:
   • Победители поступают без экзаменов
   • Действует в год проведения и следующий год

6️⃣ МегаШкола ИТМО:
   • Лекции и мастер-классы по актуальным направлениям
   • Победители поступают без экзаменов

📅 Даты вступительного экзамена:
   • Уточняйте на официальном сайте программы

💰 Стоимость обучения: {program.cost or 'Уточняйте на сайте'}
🏠 Общежитие: {'Доступно' if program.dormitory else 'Недоступно'}
"""

        return admission_info


def test_analyzer():
    """Тестирует анализатор"""
    print('🧪 Тестирование анализатора программ...')

    # Создаем тестовые данные
    test_courses = [
        Course('Машинное обучение', 6, 1, 'обязательная'),
        Course('Глубокое обучение', 6, 2, 'обязательная'),
        Course('Обработка естественного языка', 4, 2, 'выборная'),
        Course('Компьютерное зрение', 4, 2, 'выборная'),
        Course('Анализ данных', 4, 1, 'обязательная'),
        Course('Статистика и вероятности', 4, 1, 'обязательная'),
        Course('Программирование на Python', 4, 1, 'обязательная'),
        Course('Нейронные сети', 6, 2, 'обязательная'),
        Course('Этика ИИ', 2, 3, 'факультативная'),
        Course('Проектная работа', 8, 3, 'обязательная'),
        Course('Магистерская диссертация', 12, 4, 'обязательная'),
    ]

    test_programs = [
        Program(
            name="Магистратура 'Искусственный интеллект'",
            url='https://abit.itmo.ru/program/master/ai',
            description='Создавайте AI-продукты и технологии, которые меняют мир.',
            duration=4,
            courses=test_courses,
            total_credits=sum(c.credits for c in test_courses),
            institute='Институт прикладных компьютерных наук',
            form='очная',
            language='русский',
            cost='599 000 ₽',
            dormitory=True,
            military_center=True,
            accreditation=True,
        ),
        Program(
            name="Магистратура 'AI Product Management'",
            url='https://abit.itmo.ru/program/master/ai_product',
            description='Управляйте AI-продуктами и бизнес-процессами.',
            duration=4,
            courses=test_courses,  # Используем те же курсы для простоты
            total_credits=sum(c.credits for c in test_courses),
            institute='Институт прикладных компьютерных наук',
            form='очная',
            language='русский',
            cost='599 000 ₽',
            dormitory=True,
            military_center=True,
            accreditation=True,
        ),
    ]

    analyzer = ProgramAnalyzer(test_programs)

    # Тестируем сравнение программ
    print('\n📊 Сравнение программ:')
    print(analyzer.get_program_comparison())

    # Тестируем рекомендации для разных бэкграундов
    test_backgrounds = [
        'У меня есть опыт в программировании на Python и математике, работаю в сфере разработки',
        'Я работаю в сфере бизнеса и менеджмента, есть опыт управления проектами',
        'У меня техническое образование и опыт в разработке, интересуюсь наукой',
        'я не знаю питон',
        'математик',
    ]

    for background in test_backgrounds:
        print(f"\n💡 Рекомендации для бэкграунда: '{background}'")
        recommendations = analyzer.get_course_recommendations(background)
        print(recommendations)


if __name__ == '__main__':
    test_analyzer()
