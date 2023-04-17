import json
import os
import time
from Classes.classes_api import HeadHunterAPI, SuperJobAPI
from src.utils import convert_to_rub, print_vacancy, get_vacancies_by_salary, format_text, remove_none_salary_min, \
    remove_none_salary_max, remove_none_salary, get_top_vacancies, get_keyword_responsibility_vacancies, \
    get_keyword_requirement_vacancies


class JSONSaver:

    def __init__(self):
        self.keyword = None
        self.__filename = None
        self.__filename_sort = None

    @property
    def filename(self):
        return self.__filename

    @property
    def filename_sort(self):
        return self.__filename_sort

    def add_vacancies(self, data) -> None:
        """
        Добавляет список вакансий в файл в формате JSON.
        Аргументы:
        - data: список словарей, каждый словарь представляет информацию о вакансии.
        Возвращает:
        - None
        """
        # проверяем, существует ли файл с заданным именем и проверяем, что файл не пустой
        # и проверяем, что файл был изменен не ранее, чем 1 час назад
        if os.path.exists(self.__filename) and os.path.getsize(self.__filename) > 0 \
                and time.time() - os.path.getmtime(self.__filename) <= 60 * 60:
            #  открываем файл для записи
            with open(self.__filename, 'w', encoding='utf-8') as file:
                #  записываем данные в файл в формате JSON с отступом в 4 пробела
                json.dump(data, file, indent=4)

    def add_vacancies_forced(self, data) -> None:
        """
        Форсированно добавляет список вакансий в файл в формате JSON.
        Аргументы:
        - data: список словарей, каждый словарь представляет информацию о вакансии.
        Возвращает:
        - None
        """
        #  открываем файл для записи
        with open(self.__filename_sort, 'w', encoding='utf-8') as file:
            #  записываем данные в файл в формате JSON с отступом в 4 пробела
            json.dump(data, file, indent=4)

    def sort_json_HH(self, data):
        """
        Сортирует и сохраняет полученные данные в файл.
        Args:
            data: данные, которые необходимо отсортировать и сохранить.
        Returns:
            None
        """
        # считываем данные из файла с неотсортированными данными, полученными от API
        data = data
        # Открываем файл для записи
        with open(self.__filename_sort, 'w', encoding='utf-8') as file_w:
            # Создаем пустой список для хранения отсортированных вакансий
            vacancies = []
            # Проходимся по каждому элементу из неотсортированных данных
            for item in data:
                # Инициализируем переменные salary_min, salary_max и currency значением None
                salary_min, salary_max, currency = None, None, None
                # Если информация о зарплате доступна, получаем ее значения
                if item["salary"]:
                    salary_min, salary_max, currency = item["salary"]["from"], \
                                                       item["salary"]["to"], item["salary"]["currency"]
                    # Если валюта зарплаты не RUR, то конвертируем ее в RUR
                    if item["salary"]["currency"] != "RUR" and not None:
                        salary_min, currency = convert_to_rub(item["salary"]["currency"],
                                                              salary_min) if item["salary"]["from"] else (None, None)
                        salary_max, currency = convert_to_rub(item["salary"]["currency"],
                                                              salary_max) if item["salary"]["to"] else (None, None)
                        currency = "RUR"

                # Обработка формата для поля responsibility/requirement
                convert_responsibility = format_text(item["snippet"]["responsibility"])
                convert_requirement = format_text(item["snippet"]["requirement"])

                # Создаем объект Vacancy с полученными данными и добавляем его в список vacancies
                vacancy_pars = Vacancy(item["name"], salary_min, salary_max, currency,
                                       item["employer"]["name"], item["alternate_url"], convert_responsibility,
                                       convert_requirement)
                vacancies.append(vacancy_pars.Vacancy_Pars())

            # Сохраняем отсортированные данные в файл в формате JSON
            json.dump(vacancies, file_w, indent=4)
        return vacancies

    def sort_json_SJ(self, data):
        """
        Сортирует и сохраняет полученные данные в файл.
        Args:
            data: данные, которые необходимо отсортировать и сохранить.
        Returns:
            None
        """
        # считываем данные из файла с неотсортированными данными, полученными от API
        data = data
        # Открываем файл для записи
        with open(self.__filename_sort, 'w', encoding='utf-8') as file_w:
            # Создаем пустой список для хранения отсортированных вакансий
            vacancies = []
            # Проходимся по каждому элементу из неотсортированных данных
            for item in data:
                # Если информация о зарплате доступна, получаем ее значения
                if item["payment_from"] == 0:
                    item["payment_from"] = None
                if item["payment_to"] == 0:
                    item["payment_to"] = None

                salary_min, salary_max, currency = item["payment_from"], item["payment_to"], item["currency"]

                # Обработка формата для поля responsibility/requirement
                convert_responsibility = format_text(item["candidat"])
                convert_requirement = format_text(item["work"])

                # Создаем объект Vacancy с полученными данными и добавляем его в список vacancies
                vacancy_pars = Vacancy(item["profession"], salary_min, salary_max, currency,
                                       item["firm_name"], item["link"], convert_responsibility,
                                       convert_requirement)
                vacancies.append(vacancy_pars.Vacancy_Pars())

            # Сохраняем отсортированные данные в файл в формате JSON
            json.dump(vacancies, file_w, indent=4)
        return vacancies

    def sorted_salary_min(self) -> list[dict]:
        """
        Возвращает отсортированный по возрастанию список словарей вакансий из файла, отсортированного методом
        sort_json_HH, в котором каждый словарь представляет одну вакансию. Вакансии отсортированы по значению
        salary_min, при условии, что это значение не равно None. Вакансии, у которых значение salary_min равно None,
        перемещаются в конец списка.
        :return: list[dict] - отсортированный список словарей вакансий
        """
        with open(self.__filename_sort, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return sorted(data, key=lambda x: x['salary_min'] if x['salary_min'] is not None else float('-inf'))

    def sorted_salary_max(self):
        """
        Возвращает отсортированный по возрастанию список словарей вакансий из файла, отсортированного методом
        sort_json_HH, в котором каждый словарь представляет одну вакансию. Вакансии отсортированы по значению
        salary_max, при условии, что это значение не равно None. Вакансии, у которых значение salary_max равно None,
        перемещаются в конец списка. :return: list[dict] - отсортированный список словарей вакансий
        """
        with open(self.__filename_sort, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return sorted(data, key=lambda x: x['salary_max'] if x['salary_max'] is not None else float('-inf'))

    def remove_sorted_json(self) -> dict:
        """
        Читает и возвращает содержимое файла с отсортированными вакансиями в формате JSON.
        :return: Содержимое файла с отсортированными вакансиями в формате словаря Python.
        :rtype: dict
        """
        with open(self.__filename_sort, 'r', encoding='utf-8') as file:
            return json.load(file)

    def run_vacancy_functions(self):
        """Запускает цикл выбора действий для работы с вакансиями.

        Аргументы:
        self: Экземпляр класса, содержащий параметры для работы с API HeadHunter и SuperJob.

        Возвращает:
        None.
        """
        data = None
        data_need = False
        api_dict = {
            6: "1: Ввести ключевое слово для поиска",
            1: "2: Загрузить данные из HeadHunter по ключевому слову",
            2: "3: Загрузить недавние данные из HeadHunter по ключевому слову",
            3: "4: Загрузить данные из SuperJob по ключевому слову",
            4: "5: Загрузить недавние данные из SuperJob по ключевому слову",
            5: "6: Работа с данными",
            9: "9: Выход"

        }
        def_dict = {
            1: "1: Отсортировать по мнимальной зарплате",
            2: "2: Отсортировать по максимальной зарплате",
            3: "3: Вывести весь список без сортировки",
            4: "4: Отсортировать по зарплате с введёнными параметрами",
            5: "5: Отсортировать по отсутствию нижней планки зарплаты",
            6: "6: Отсортировать по отсутствию верхней планки зарплаты",
            7: "7: Отсортировать по отсутствию нижней и верхней планок зарплаты",
            8: "8: Отсортировать список по минимальной зарплате и вывести n лучших результатов",
            9: "9: Отсортировать весь список по максимальной зарплате и вывести n лучших результатов",
            10: "10: Отсортировать весь список по ключевому слову в обязанностях",
            11: "11: Отсортировать весь список по ключевому слову в требованиях",
            20: "20: Выход",
        }
        while True:

            for i in api_dict.values():
                print(i)
            if self.keyword is None:
                print("\nСначала введите ключевое слово для поиска вакансий")
            if data_need:
                print("Сначала загрузите данные c одного из сайтов")
                data_need = False

            count_def = input(f"Выберите действие: ")
            # Если выбран пункт 1, запрашивается ключевое слово для поиска вакансий и создаются файлы
            # для хранения отсортированных данных.
            if count_def == "1":
                self.keyword = input("Введите ключевое слово для поиска вакансий: ")
                self.__filename_sort = f"{self.keyword.title()}_sort.json"
                self.__filename = f"{self.keyword.title()}.json"

            # Если выбран пункт 2, запрашивается количество вакансий для загрузки и вызывается метод
            # для получения вакансий с помощью API HeadHunter.
            # Полученные данные сортируются сохраняются в файл.
            if count_def == "2" and self.keyword is not None:
                # keyword = input("Введите ключевое слово для поиска вакансий: ")
                hh_api = HeadHunterAPI(self.keyword)
                data_vacan = input("Сколько вакансий загрузить? ")
                try:
                    data = hh_api.get_vacancies_HH(int(data_vacan))
                    data = self.sort_json_HH(data)
                except ValueError:
                    print("Данные введены не верно")

            # Если выбран пункт 3, вызывается метод для получения вакансий с HeadHunter записанные в файл.
            # Полученные данные берутся из фала если он есть и выводится количество найденных вакансий.
            if count_def == "3" and self.keyword is not None:
                # keyword = input("Введите ключевое слово для поиска вакансий: ")
                hh_api = HeadHunterAPI(self.keyword)
                try:
                    data = hh_api.get_vacancies_HH(0, True)
                    data = self.sort_json_HH(data)
                    print(f"Найдено {len(data)} вакансий")
                except ValueError:
                    print("Данные введены не верно")

            # Если выбран пункт 4, запрашивается количество вакансий для загрузки и вызывается метод
            # для получения вакансий с помощью API SuperJob.
            # Полученные данные сортируются сохраняются в файл.
            if count_def == "4" and self.keyword is not None:
                superjob_api = SuperJobAPI(self.keyword)
                data_vacan = input("Сколько вакансий загрузить? ")
                try:
                    data = superjob_api.get_vacancies_SJ(int(data_vacan))
                    data = self.sort_json_SJ(data)
                except ValueError:
                    print("Данные введены не верно")

            # Если выбран пункт 5, вызывается метод для получения вакансий с SuperJob записанные в файл.
            # Полученные данные берутся из фала если он есть и выводится количество найденных вакансий.
            elif count_def == "5" and self.keyword is not None:
                # keyword = input("Введите ключевое слово для поиска вакансий: ")
                superjob_api = SuperJobAPI(self.keyword)
                try:
                    data = superjob_api.get_vacancies_SJ(0, True)
                    data = self.sort_json_SJ(data)
                    print(f"Найдено {len(data)} вакансий")
                except ValueError:
                    print("Данные введены не верно")

            if data is None or data == []:
                if count_def == "6":
                    data_need = True
            elif data is not None and count_def == "6" and data != []:
                while count_def != "20":

                    for i in def_dict.values():
                        print(i)
                    count_def = input(f"Выберите действие: ")
                    if count_def.isdigit():
                        # Сортировать вакансии по зарплате по возрастанию
                        if count_def == "1":
                            print_vacancy(self.sorted_salary_min())
                        # Сортировать вакансии по зарплате по убыванию
                        elif count_def == "2":
                            print_vacancy(self.sorted_salary_max())
                        # Вывести все полученные вакансии
                        elif count_def == "3":
                            print_vacancy(data)
                        # Вывести вакансии с заданной зарплатой
                        elif count_def == "4":
                            print_vacancy(get_vacancies_by_salary(data))
                        # Удалить вакансии, у которых не указана минимальная зарплата
                        elif count_def == "5":
                            print_vacancy(remove_none_salary_min(data))
                        # Удалить вакансии, у которых не указана максимальная зарплата
                        elif count_def == "6":
                            print_vacancy(remove_none_salary_max(data))
                        # Удалить вакансии, у которых не указана зарплата
                        elif count_def == "7":
                            print_vacancy(remove_none_salary(data))
                        # Вывести топ-n вакансий по минимальной зарплате
                        elif count_def == "8":
                            print_vacancy(get_top_vacancies(self.sorted_salary_min()))
                        # Вывести топ-n вакансий по максимальной зарплате
                        elif count_def == "9":
                            print_vacancy(get_top_vacancies(self.sorted_salary_max()))
                        # Вывести вакансии, содержащие заданные ключевые слова в обязанностях
                        elif count_def == "10":
                            print_vacancy(get_keyword_responsibility_vacancies(data))
                        # Вывести вакансии, содержащие заданные ключевые слова в требованиях
                        elif count_def == "11":
                            print_vacancy(get_keyword_requirement_vacancies(data))

            if count_def == "9":
                break


class Vacancy:
    """
    Класс Vacancy представляет вакансию и ее характеристики.

    Атрибуты:
    - name_job (str): название вакансии
    - salary_min (float): минимальная зарплата
    - salary_max (float): максимальная зарплата
    - currency (str): валюта зарплаты
    - employer (str): работодатель
    - link (str): ссылка на вакансию
    - responsibility (str): обязанности по вакансии
    - requirement (str): требования к кандидату

    Методы:
    - Vacancy_Pars(): возвращает словарь характеристик вакансии
    """

    __slots__ = (
        "name_job", "salary_min", "salary_max", "currency", "employer", "link", "responsibility", "requirement")

    def __init__(self, name_job, salary_min, salary_max, currency, employer, link, responsibility, requirement):
        self.requirement = requirement
        self.responsibility = responsibility
        self.name_job = name_job
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.currency = currency
        self.employer = employer
        self.link = link

    def Vacancy_Pars(self):
        """
        Возвращает словарь характеристик вакансии.
        """
        Vacancy_Pars = {
            "name_job": self.name_job,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "employer": self.employer,
            "link": self.link,
            "responsibility": self.responsibility.lower(),
            "requirement": self.requirement.lower(),
        }
        return Vacancy_Pars