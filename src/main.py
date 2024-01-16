from tabulate import tabulate
from src.classes import HeadHunterAPI, DBManager


def main():
    # Получаем пароль от базы данных, запрашиваем имя для сохранения
    pass_ = input('Привет! Введите Ваш пароль от базы данных postgres: ')
    name_db = input('Введите имя для сохранения базы данных или нажмите '
                    '"ENTER" для имени по умолчанию: ').strip()
    if name_db == '' or list(name_db)[0].isdigit():
        # Создаем экземпляр класса Dbmanager, для работы с базой данных имя по
        # умолчанию
        db = DBManager(pass_)
    else:
        # Создаем экземпляр класса Dbmanager, для работы с базой данных
        db = DBManager(pass_, name_db)
    # Создаем базу данных, если она не существует
    db.creat_db()
    # Создаем экземпляр класса для работы с API HeadHunter
    hh = HeadHunterAPI()
    # Получаем список вакансий
    vac_list = hh.get_vacancies()
    # Получаем список работодателей
    emp_list = hh.get_employers()

    # Создаем две таблицы (с вакансиями и с работодателями), заполняем из
    # списков вакансий и работодателей, полученных от HeadHunter
    db.creat_table_employers_tab()
    db.instance_emp_from_lst(emp_list)
    db.creat_table_vacancies_tab()
    db.instance_vac_from_lst(vac_list)

    # Вывод информации
    data_1 = db.get_companies_and_vacancies_count()
    print('\033[1;34mСПИСОК ВСЕХ КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ У КАЖДОЙ '
          'КОМПАНИИ:\033[0m')
    print(tabulate(data_1, headers=['Работодатель', 'Количество вакансий'],
                   tablefmt='fancy_grid'))
    input('\033[1;92mНажмите "ENTER" для продолжения <--|\033[0m')
    data_2 = db.get_all_vacancies()
    print('\033[1;34mВСЕ ВАКАНСИИ:\033[0m')
    print(
        tabulate(data_2, headers=['Работодатель', 'Вакансия', 'Зарплата от - '
                                                              'до ', 'url'],
                 tablefmt='fancy_grid'))
    input('\033[1;92mНажмите "ENTER" для продолжения <--|\033[0m')
    data_3 = db.get_avg_salary()
    print('\n\033[1;34mСРЕДНЯЯ ЗАРПЛАТА\033[0m')
    print(tabulate(data_3, headers=['Средняя зарплата от', 'Средняя зарплата до'],
                   tablefmt='fancy_grid'))
    input('\033[1;92mНажмите "ENTER" для продолжения <--|\033[0m')
    data_4 = db.get_vacancies_with_higher_salary()
    print(
        '\033[1;34mВСЕ ВАКАНСИИ, У КОТОРЫХ "ЗАРПЛАТА ОТ" ВЫШЕ СРЕДНЕЙ:\033[0m')
    print(tabulate(data_4,
                   headers=['Работодатель', 'Вакансия', 'Зарплата от', 'url'],
                   tablefmt='fancy_grid'))
    # Запрашиваем слово для поиска в вакансиях
    keyword = input(
        '\n\033[1;34mВведите ключевое слово для поиска в вакансиях: '
        '\033[0m').strip().lower()
    data_5 = db.get_vacancies_with_keyword(keyword)
    if len(data_5) != 0:
        print(tabulate(data_5, headers=['Работодатель', 'Вакансия',
                                        'url', 'Зарплата от', 'Город',
                                        'Описание'], tablefmt='fancy_grid'))
    else:
        print('\033[1;31mНичего не нашлось!\033[0m')


if __name__ == '__main__':
    main()