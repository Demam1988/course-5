import fake_useragent


vacancies_on_page = 100
pages = 20

employers_id = {
        "Сбербанк России": 3529,
        "Webtronics": 5843588,
        "ООО СФЕРА": 4402893,
        "ООО АЙТИ.СПЕЙС": 2000762,
        "Convergent": 57862,
        "AERODISK ": 2723603,
        "Digital Reputation": 3183420,
        "Точка": 2324020,
        "ВТБ": 4181,
        "ООО 24Н Софт": 2515455
    }

headers = {'user-agent': fake_useragent.UserAgent().random}
params = {'employer_id': employers_id.values(), 'per_page': vacancies_on_page,
          'archive': False}