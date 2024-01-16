CREATE DATABASE vac;

CREATE TABLE IF NOT EXISTS employers_tab(
            employer_id int PRIMARY KEY,
            employer_name varchar(255),
            employer_url varchar(255),
            open_vac int);

CREATE TABLE IF NOT EXISTS vacancies_tab(
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
            date_pub date;

TRUNCATE TABLE employers_tab CASCADE;

INSERT INTO employers_tab VALUES (%s, %s, %s, %s), (emp['employer_id'],
                                                    emp['employer_name'],
                                                    emp['url'],
                                                    emp['open_vac']);

INSERT INTO vacancies_tab VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s),
                            (vac['vacancy_id'], vac['employer_id'],
                             vac["title"], vac['url'], vac['salary_from'],
                             vac['salary_to'], vac['currency'],
                             vac['description'], vac['town'], vac['education'],
                             vac['experience'], vac['date_pub']);

SELECT employer_name, COUNT(*) as total
                FROM vacancies_tab
                RIGHT JOIN employers_tab
                USING(employer_id)
                GROUP BY employer_name
                ORDER BY total DESC;

SELECT employer_name, title, CONCAT('от ', salary_from,
                    ' до ', salary_to, ' ', vacancies_tab.currency) as salaryrl, url
                    FROM vacancies_tab
                    JOIN employers_tab USING(employer_id)
                    ORDER BY employer_name;

select round(AVG(salary_from)) as от,
                        (select round(AVG(salary_to)) as до
                        from vacancies_tab where salary_to <> 0)
                        from vacancies_tab
                        where salary_from <>0;

select employer_name, title, salary_from, url
                            from vacancies_tab
                            rigth join employers_tab USING(employer_id)
                            where salary_from > (SELECT AVG(salary_from)
                                                 FROM vacancies_tab WHERE
                                                 salary_from <> 0)
                            order by employer_name;

SELECT employer_name, title, url, salary_from,
                        town, description
                        FROM vacancies_tab
                        rigth join employers_tab USING(employer_id)
                        WHERE lower(title) LIKE '%{keyword}%'
                        OR lower(description) LIKE '%{keyword}%'
                        OR lower(town) LIKE '%{keyword}%';