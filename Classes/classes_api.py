import json
from abc import ABC
import requests

from src.utils import check_last_updated, remove_duplicate_vacancies


class Engine(ABC):
    def get_request(self, page, count=100):
        pass


class HeadHunterAPI(Engine):

    def __init__(self, keyword):
        self.keyword = keyword

    def get_request_HH(self, page, count=100):
        params = {
            "text": self.keyword,
            "page": page,
            "per_page": count,
        }
        return requests.get("https://api.hh.ru/vacancies", params=params).json()["items"]

    def get_vacancies_HH(self, count=100, need=False):
        """
        Получает вакансии с сайта HH.ru с использованием API и возвращает список словарей с информацией о каждой
        вакансии.

        Аргументы:
        - self: экземпляр класса HHParser
        - count (int): количество запрашиваемых вакансий, по умолчанию 100
        - need (bool): флаг необходимости обновления данных из файла, по умолчанию False

        Возвращает:
        - data (list): список словарей с информацией о каждой вакансии

        """
        # имя файла куда будут записываться данные
        file_name = f"{self.keyword.title()}_HH.json"
        data = []
        # проверка на необходимость обновления данных из файла
        if check_last_updated(file_name) and need:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
        # если данных не хватает, делаем запрос на HH
        if len(data) < count:
            print("Делаем запрос с HEAD HUNTER")
            count_pages = count // 100
            new_count = 100
            response = []

            # проходим по страницам, запрашивая вакансии
            for page in range(count_pages + 1):
                count_values = count - page * 100
                if count_values > 0:
                    if count_values < new_count:
                        new_count = count_values
                    print(f"Парсинг страницы {page + 1}", end=": ")
                    values = self.get_request_HH(page, new_count)
                    print(f"Найдено {len(values)} вакансий.")
                    response.extend(values)
                    response = remove_duplicate_vacancies(response)

                # response_unique = list(
                #     {vacancy['id']: vacancy for vacancy in response}.values())

            print(f"Найдено всего {len(response)} уникальных вакансий.")
            # если вакансии найдены, записываем их в файл
            if len(response) > 0:
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(response, file, indent=4)
            data = response
        return data


class SuperJobAPI(Engine):

    def __init__(self, keyword):
        self.keyword = keyword
        self.api_key = "v3.r.137487603.2e7c67033992d82c8e1eb1d18f4f97eb738b899a" \
                       ".0b192f0633fd83104c248f8dec42f7d957df82a1 "

    def get_request_SJ(self, page_number, count=100):
        url_super_job = "https://api.superjob.ru/2.0/vacancies/"
        headers = {'X-Api-App-Id': self.api_key}
        params = {"keywords": self.keyword,
                  "count": count,
                  "page": page_number,
                  }
        return requests.get(url_super_job, headers=headers, params=params)

    def get_vacancies_SJ(self, count=100, need=False):
        """
        Получает данные о вакансиях с сайта SuperJob.ru по заданному ключевому слову.

        :param count: количество запрашиваемых вакансий (по умолчанию 100)
        :type count: int
        :param need: флаг, указывающий на необходимость обновления данных из файла кэша (по умолчанию False)
        :type need: bool
        :return: список словарей с данными о вакансиях
        :rtype: list
        """
        # имя файла куда будут записываться данные
        file_name = f"{self.keyword.title()}_SJ.json"
        data = []
        if check_last_updated(file_name) and need:
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
        if len(data) < count:
            # Иначе производится парсинг сайта.
            print("Делаем запрос с SUPER JOB")
            count_pages = count // 100
            new_count = 100
            response = []
            for page in range(count_pages + 1):
                count_values = count - page * 100
                if count_values > 0:
                    if count_values < new_count:
                        new_count = count_values
                    print(f"Парсинг страницы {page + 1}", end=": ")
                    values = self.get_request_SJ(page, new_count)
                    vacancies = values.json()["objects"]
                    print(f"Найдено {len(vacancies)} вакансий.")
                    response.extend(vacancies)
                    response = remove_duplicate_vacancies(response)

            print(f"Найдено всего {len(response)} вакансий.")
            if len(response) > 0:
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(response, file, indent=4)
            data = response
        return data