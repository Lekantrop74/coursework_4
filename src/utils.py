import json
import os
import time
import requests


def convert_to_rub(currency_code: str, amount: float) -> tuple:
    """
    Преобразует заданную сумму валюты в российские рубли (RUR) используя курс валют Центрального Банка России.
    :param currency_code: Строковое значение, представляющее код валюты для преобразования (например, "USD", "EUR").
    :param amount: Вещественное число, представляющее сумму валюты для преобразования.
    :return: Кортеж, содержащий целое число, представляющее преобразованную сумму в российских рублях, и строку,
             представляющую код российских рублей ("RUR").
    """
    if not check_last_updated("exchange_rate.json", False):
        # Если курс валют не был обновлен или ранее сохраненный курс устарел, получаем его с сервера ЦБ РФ
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        if response.status_code == 200:
            # Если запрос успешен, сохраняем полученные данные в файл "exchange_rate.json"
            data_exchange_rate = response.json()
            with open("exchange_rate.json", 'w', encoding='utf-8') as file_w:
                json.dump(data_exchange_rate, file_w, indent=4)
    else:
        # Если ранее сохраненный курс валют не устарел, загружаем его из файла "exchange_rate.json"
        with open("exchange_rate.json", 'r', encoding='utf-8') as file_r:
            data_exchange_rate = json.load(file_r)

    try:
        # Получаем текущий курс заданной валюты и ее номинал
        currency_rate = data_exchange_rate["Valute"][currency_code.upper()]["Value"]
        currency_Nominal = data_exchange_rate["Valute"][currency_code.upper()]["Nominal"]
        # Конвертируем заданную сумму в рубли по текущему курсу
        rub_amount = amount * currency_rate / currency_Nominal
        if rub_amount is not None:
            # Задаем код валюты "RUR" и округляем сконвертированную сумму до целого числа
            currency_code = "RUR"
            rub_amount = int(rub_amount)
            # Возвращаем сконвертированную сумму и код валюты "RUR"
            return rub_amount, currency_code
    except KeyError:
        # Если не удалось получить курс заданной валюты, возвращаем исходные аргументы
        return amount, currency_code


def check_last_updated(file_name: str, need_check=True) -> bool:
    """
    Функция проверяет, обновлялись ли данные в файле с указанным именем за последний час.
    Если данные обновлялись менее часа назад, то функция возвращает True и выводит сообщение об этом.
    Если данные обновлялись более часа назад или файла не существует, то функция возвращает False.

    :param file_name: имя файла, данные в котором проверяются на наличие обновлений
    :param need_check: флаг, указывающий, нужно ли выводить сообщение о том, что обновление не требуется
    :return: результат проверки (True, если данные обновлялись менее часа назад, False - в противном случае)
    """
    last_updated_file = "last_updated.json"

    # Проверяем наличие файла с датой последнего обновления и, если он есть, загружаем его
    if os.path.exists(last_updated_file):
        with open(last_updated_file, 'r') as f:
            try:
                last_updated = json.load(f)
            except json.JSONDecodeError:
                last_updated = {}
    else:
        last_updated = {}

    # Проверяем, был ли файл с данными обновлен за последний час а также наличие файла и его размер
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0 \
            and file_name in last_updated and time.time() - last_updated[file_name] <= 60 * 60:
        if need_check:
            print(f"Данные \'{file_name}\' обновлялись меньше часа назад. А точнее "
                  f"{int(time.time() - last_updated[file_name]) // 60} минут и "
                  f"{int(time.time() - last_updated[file_name]) % 60} секунд назад. Обновления не требуется")
        last_updated[file_name] = time.time()
        return True
    else:
        # Если данные не были обновлены, то записываем текущую дату и время в файл с датами обновления
        last_updated[file_name] = time.time()
        with open(last_updated_file, "w") as f:
            json.dump(last_updated, f, indent=4)
        return False


def print_vacancy(data):
    """Функция принимает список данных о вакансиях и выводит на экран информацию о каждой вакансии.
    Аргументы:
    data -- список словарей, каждый словарь содержит информацию о конкретной вакансии
    Вывод:
    Функция выводит на экран информацию о каждой вакансии, включая название вакансии, зарплату, ссылку на вакансию,
    требования и обязанности."""

    count = 0
    for i in data:
        # Проверяем, является ли текущий элемент словарём
        if isinstance(i, dict):
            # Формируем строку с минимальной зарплатой, если она указана
            salary_min = f"От {i['salary_min']} " if i['salary_min'] else ""
            # Формируем строку с минимальной зарплатой, если она указана
            salary_max = f"До {i['salary_max']} " if i['salary_max'] else ""
            # Получаем валюту, в которой указана зарплата
            currency = i['currency'] if i['currency'] else ""
            # Если зарплата не указана, выводим соответствующее сообщение
            if salary_min == "" and salary_max == "":
                salary_min = "Не указано"
            # Выводим информацию о вакансии
            print("=" * 50)
            print(f"Наниматель: {i['employer']} \nДолжность: {i['name_job']}"
                  f" \nЗарплата: {salary_min}{salary_max} {currency}\nСсылка на вакансию: {i['link']}\n"
                  f"Обязанности: {i['responsibility']}\n"
                  f"Требования: {i['requirement']}")

            count += 1
    # Выводим общее число найденных вакансий
    print(f"\nВсего {count} результатов")


def get_vacancies_by_salary(data):
    """
    Функция получает список вакансий и фильтрует его по указанным минимальной и максимальной зарплате.
    Результаты фильтрации выводятся на экран при помощи функции print_vacancy.

    :param data: список вакансий, который нужно отфильтровать
    :return: нет
    """
    try:
        salary_min = int(input("Введите минимальную зарплату: "))
        salary_max = int(input("Введите максимальную зарплату: "))
        sort_salary = []
        for vacancy in data:
            if vacancy['salary_min'] and vacancy['salary_min'] >= salary_min and vacancy['salary_max'] and \
                    vacancy['salary_max'] <= salary_max:
                sort_salary.append(vacancy)
        print_vacancy(sort_salary)
    except ValueError:
        print("Ошибка ввода. Введите число.")


def remove_none_salary_min(data):
    """
    Удаляет вакансии, где минимальная зарплата равна None.
    :param data: словарь с данными о вакансиях
    :return: измененный словарь
    """
    new_data = []
    for item in data:
        if item['salary_min'] is not None:
            new_data.append(item)
    return new_data


def remove_none_salary_max(data):
    """
    Удаляет вакансии, где максимальная зарплата равна None.
    :param data: словарь с данными о вакансиях
    :return: измененный словарь
    """
    new_data = []
    for item in data:
        if item['salary_max'] is not None:
            new_data.append(item)
    return new_data


def remove_none_salary(data):
    """
    Удаляет вакансии, где одна из зарплат равна None.
    :param data: словарь с данными о вакансиях
    :return: измененный словарь
    """
    new_data = []
    for item in data:
        if item['salary_min'] is not None and item['salary_max'] is not None:
            new_data.append(item)
    return new_data


def get_top_vacancies(data):
    """
    Функция получает список вакансий и запрашивает у пользователя количество выводимых вакансий.
    Затем функция выводит указанное количество последних вакансий из списка.
    :param data: список вакансий
    :return: список последних n вакансий, где n - количество, указанное пользователем
    """
    try:
        n = int(input("Введите количество выводимых вакансий: "))
        if n <= 0:
            return []
        new_data = []
        for i, item in enumerate(data[::-1]):
            new_data.insert(0, item)
            if i == n - 1 or i == len(data) - 1:
                return new_data
    except ValueError:
        print("Некорректный ввод, попробуйте еще раз")
        return []


def format_text(text: str) -> str:
    """
    Удаление ненужных букв в полях
    :param text: Строка для форматирования
    :return: Отформатированная строка
    """
    patterns = {
        1: ['<highlighttext>', ''],
        2: ['</highlighttext>', '']
    }

    if text == "null":
        return f"Данных нет"
    elif text is None:
        return f"Данных нет"
    else:
        for i in patterns:
            text = text.replace(patterns[i][0], patterns[i][1])
        return text


def get_keyword_responsibility_vacancies(data):
    """Функция получает список вакансий и запрашивает у пользователя ключевое слово для фильтрации по обязанностям.
    Возвращает список вакансий, где в описании обязанностей встречается заданное ключевое слово.
    Аргументы: - data: список вакансий, для которых будет произведен поиск.
    Возвращает: - new_data: список вакансий, содержащих заданное ключевое слово в описании обязанностей.
    Если произошла ошибка ввода, возвращает пустой список."""
    try:
        # Запрашиваем у пользователя ключевое слово
        keyword = input("Введите ключевое слово для фильтрации по обязанностям: ")

        # Создаем новый список вакансий
        new_data = []

        # Проходимся по каждой вакансии в списке data
        for i in data:
            # Если в описании обязанностей встречается заданное ключевое слово
            if keyword in i['responsibility']:
                # Добавляем вакансию в новый список
                new_data.append(i)

        # Возвращаем отфильтрованный список вакансий
        return new_data
    except ValueError:
        # В случае ошибки ввода возвращаем пустой список
        print("Некорректный ввод, попробуйте еще раз")
        return []


def get_keyword_requirement_vacancies(data):
    """
    Функция принимает список вакансий и фильтрует его по ключевому слову в требованиях.
    Аргументы:
    - data (list): список словарей, где каждый словарь представляет собой вакансию со следующими ключами:
        * title (str): название вакансии;
        * responsibility (str): перечень обязанностей;
        * requirement (str): перечень требований.
    Возвращает отфильтрованный список вакансий, удовлетворяющих требованию.
    Если произошла ошибка при вводе ключевого слова, функция вернет пустой список.
    """
    try:
        keyword = input("Введите ключевое слово для фильтрации по требованиям: ")
        new_data = []
        # Проходим по списку вакансий
        for i in data:
            # Если ключевое слово содержится в перечне требований
            if keyword in i['requirement']:
                # Добавляем вакансию в отфильтрованный список
                new_data.append(i)
        return new_data
    except ValueError:
        # Если возникла ошибка, сообщаем об этом и возвращаем пустой список
        print("Некорректный ввод, попробуйте еще раз")
        return []

def remove_duplicate_vacancies(vacancies):
    unique_vacancies = {}
    for vacancy in vacancies:
        if vacancy["id"] not in unique_vacancies:
            unique_vacancies[vacancy["id"]] = vacancy
    return list(unique_vacancies.values())