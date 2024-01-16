import requests
import fake_useragent
import psycopg2
from src.variables import vacancies_on_page, employers_id, pages


class HeadHunterAPI:
    """ Класс для работы с вакансиями с HeadHunter """

    headers = {'user-agent': fake_useragent.UserAgent().random}
    params = {'per_page': vacancies_on_page, 'employer_id':
              employers_id.values(), 'archive': False}

    def get_employers(self):
        """
        Получение списка работодателей. Выходные данные в формате списка
        словарей Python - работа с requests и JSON. (id работодателей в
        словаре employers_id в файле variables.py).
        """

        self.params["only_with_vacancies"] = True
        emp_list_hh = []
        for id_ in employers_id.values():
            response = requests.get(f"https://api.hh.ru/employers/"
                                    f"{id_}", params=self.params,
                                    headers=self.headers).json()

            employers_dic = {'employer_id': response['id'], 'employer_name':
                             response['name'],
                             'url': response['alternate_url'],
                             'open_vac': response['open_vacancies']}
            emp_list_hh.append(employers_dic)
        return emp_list_hh

    def get_vacancies(self):
        """
        Получение списка вакансий по интересующим работодателям.
        (id работодателей в словаре employers_id в файле variables.py. Выходные
        данные в формате списка словарей Python - работа с requests и JSON).
        """

        vac_list_hh = []
        for page in range(pages):
            self.params['page'] = page
            data_hh = requests.get(f'https://api.hh.ru/vacancies?',
                                   params=self.params,
                                   headers=self.headers).json()
            for i in range(vacancies_on_page):
                vac_dict_hh = {'vacancy_id': data_hh['items'][i]['id'],
                               'title': data_hh['items'][i]['name'],
                               'url': data_hh['items'][i]['alternate_url'],
                               'employer_id': data_hh['items'][i][
                                   'employer']['id'],
                               'employer_name': data_hh['items'][i][
                                   'employer']['name']}
                if data_hh['items'][i]['salary'] is not None:
                    vac_dict_hh['salary_from'] = data_hh['items'][i]['salary'][
                        'from']
                    vac_dict_hh['salary_to'] = data_hh['items'][i]['salary'][
                        'to']
                    vac_dict_hh['currency'] = data_hh['items'][i]['salary'][
                        'currency']
                else:
                    vac_dict_hh['salary_from'] = 0
                    vac_dict_hh['salary_to'] = 0
                    vac_dict_hh['currency'] = 'не указано'
                vac_dict_hh['description'] = data_hh['items'][i]['snippet'][
                    'responsibility']
                vac_dict_hh['town'] = data_hh['items'][i]['area']['name']
                vac_dict_hh['education'] = data_hh['items'][i]['snippet'][
                    'requirement']
                vac_dict_hh['experience'] = data_hh['items'][i]['experience'][
                    'name']
                vac_dict_hh['date_pub'] = data_hh['items'][i]['published_at']
                vac_list_hh.append(vac_dict_hh)
        return vac_list_hh


class DBManager:
    """ Класс DBManager, который подключается к БД Postgres. """

    def __init__(self, pass_, name='vac'):
        self.conn = None
        self.dbname = name
        self.pass_ = pass_
        try:
            self.conn_new_db = psycopg2.connect(
                user='postgres',
                password=self.pass_,
                host='localhost',
                port='5432')
        except psycopg2.errors.OperationalError:
            print('\033[1;31mВозможно не верный пароль. Начните заново.\033[0m')
            exit()

    def set_conn(self):
        """ Устанавливает соединение с базой данных. """

        self.conn = psycopg2.connect(
            database=self.dbname,
            user='postgres',
            password=self.pass_,
            host='localhost',
            port='5432'
        )
        return self.conn

    def creat_db(self):
        """ Создание базы данных. """

        self.conn_new_db.autocommit = True
        cur = self.conn_new_db.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname='{dbname}'".
                    format(dbname=self.dbname))
        if cur.fetchone() is None:
            cur.execute(f' CREATE DATABASE {self.dbname}')
        cur.close()
        self.conn_new_db.close()

    def creat_table_employers_tab(self):
        """ Создание таблицы по работодателям. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS employers_tab(
            employer_id int PRIMARY KEY,
            employer_name varchar(255),
            employer_url varchar(255),
            open_vac int)
            '''
                        )
        self.conn.close()

    def creat_table_vacancies_tab(self):
        """ Создание таблицы по вакансиям. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS vacancies_tab(
            vacancy_id int PRIMARY KEY,
            employer_id int REFERENCES employers_tab(employer_id) 
            on delete restrict
            on update restrict,
            title varchar(255),
            url varchar(255),
            salary_from int,
            salary_to int,
            currency varchar(15),
            description text,
            town varchar(255),
            education text,
            experience varchar(255),
            date_pub date);
            ''')
        self.conn.close()

    def instance_emp_from_lst(self, emp_list):
        """ Заполняем таблицу employers_tab из списка """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE employers_tab CASCADE")
            for emp in emp_list:
                cur.execute(
                    "INSERT INTO employers_tab VALUES (%s, %s, %s, %s)",
                    (emp['employer_id'], emp['employer_name'],
                     emp['url'], emp['open_vac']))
        self.conn.close()

    def instance_vac_from_lst(self, vac_list):
        """ Заполняем таблицу vacancies_tab из списка. """

        self.set_conn()
        self.conn.autocommit = True
        with self.conn.cursor() as cur:
            for vac in vac_list:
                cur.execute("INSERT INTO vacancies_tab VALUES (%s, %s, "
                            "%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                            (vac['vacancy_id'], vac['employer_id'],
                             vac["title"],
                             vac['url'], vac['salary_from'],
                             vac['salary_to'], vac['currency'],
                             vac['description'], vac[
                                 'town'], vac['education'],
                             vac['experience'], vac['date_pub'],
                             ))
        self.conn.close()

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой
        компании.
        """

        self.set_conn()
        with self.conn.cursor() as cur:
            cur.execute(''' 
                SELECT employer_name, COUNT(*) as total 
                FROM vacancies_tab
                RIGHT JOIN employers_tab
                USING(employer_id)
                GROUP BY employer_name
                ORDER BY total DESC
            ''')
            data = cur.fetchall()
        self.conn.close()
        return data

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании, названия
        вакансии, зарплаты и ссылки на вакансию.
        """

        self.set_conn()
        with self.conn.cursor() as cur:
            cur.execute(''' 
                    SELECT employer_name, title, CONCAT('от ', salary_from, 
                    ' до ', salary_to, ' ', vacancies_tab.currency) as salaryrl, url 
                    FROM vacancies_tab
                    JOIN employers_tab USING(employer_id)
                    ORDER BY employer_name
                    ''')
            data = cur.fetchall()
        self.conn.close()
        return data

    def get_avg_salary(self):
        """ Получает среднюю зарплату по вакансиям. """

        self.set_conn()
        with self.conn.cursor() as cur:
            cur.execute('''select round(AVG(salary_from)) as от, 
                        (select round(AVG(salary_to)) as до 
                        from vacancies_tab where salary_to <> 0)
                        from vacancies_tab
                        where salary_from <>0''')
            data = cur.fetchall()
        self.conn.close()
        return data

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых 'зарплата от' выше средней
        по всем вакансиям.
        """

        self.set_conn()
        with self.conn.cursor() as cur:
            cur.execute('''select employer_name, title, salary_from, url
                            from vacancies_tab
                            rigth join employers_tab USING(employer_id)
                            where salary_from > (SELECT AVG(salary_from) 
                            FROM vacancies_tab WHERE salary_from <> 0)
                            order by employer_name
                            ''')
            data = cur.fetchall()
        self.conn.close()
        return data

    def get_vacancies_with_keyword(self, keyword):
        """
        Получает список всех вакансий, в названии которых содержится
        переданное в метод слово, например “python” или название города и т.п.
        """

        self.set_conn()
        with self.conn.cursor() as cur:
            cur.execute(f"""SELECT employer_name, title, url, salary_from, 
                        town, description 
                        FROM vacancies_tab
                        rigth join employers_tab USING(employer_id)
                        WHERE lower(title) LIKE '%{keyword}%' 
                        OR lower(description) LIKE '%{keyword}%' 
                        OR lower(town) LIKE '%{keyword}%' """)
            data = cur.fetchall()
        self.conn.close()
        return data