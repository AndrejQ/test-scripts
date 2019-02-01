import requests
import unittest


class TestHH(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHH, self).__init__(*args, **kwargs)
        self.url = "https://api.hh.ru/vacancies"

    def _get_vacancies_json(self, params):
        response = requests.get(self.url, params={'text': params})
        return response.json()['items']

    def _get_list_of_vacancies(self, params):
        vacancies_json = self._get_vacancies_json(params)
        result = []
        for vacancy in vacancies_json:
            vacancy = str(vacancy).lower()
            result.append(vacancy)
        return result


class TestHHPositive(TestHH):
    def __init__(self, *args, **kwargs):
        super(TestHHPositive, self).__init__(*args, **kwargs)

    def test_response_status_ok(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_query_and_result_similarity(self):
        search_query = 'разработчик'
        for vacancy in self._get_list_of_vacancies(search_query):
            self.assertIn(search_query, str(vacancy))
        search_query = 'директор магазина'
        words = search_query.split()
        for vacancy in self._get_list_of_vacancies(search_query):
            for word in words:
                self.assertIn(word, vacancy)

    def test_one_space_between(self):
        for vacancy in self._get_list_of_vacancies("директор магазина"):
            self.assertRegex(
                vacancy,
                r'директор.{0,2}\sмагазин'
            )

    def test_different_word_forms(self):
        for vacancy in self._get_list_of_vacancies('продажи'):
            if 'продажи' not in vacancy:
                self.assertIn('продаж', vacancy)

    def test_except_vacancy(self):
        for vacancy in self._get_list_of_vacancies('!продажи'):
            self.assertIn('продажи', vacancy)

    def test_regexp_star(self):
        for vacancy in self._get_list_of_vacancies('Гео*'):
            self.assertRegex(vacancy, 'гео*')

    def test_synonym(self):
        vacancies_with_syn = [
            item for item in self._get_list_of_vacancies('сторожила')
            if 'сторожила' not in item
        ]
        self.assertTrue(any(['охранник' in item for item in vacancies_with_syn]))

    def test_OR_statement(self):
        for vacancy in self._get_list_of_vacancies('разработчик OR кассир'):
            self.assertTrue('разработчик' in vacancy or 'кассир' in vacancy)

    def test_AND_statement(self):
        for vacancy in self._get_list_of_vacancies('разработчик AND кассир'):
            self.assertTrue('разработчик' in vacancy and 'кассир' in vacancy)

    def test_exclusion(self):
        first, second, third = 'разработчик', 'кассир', 'менеджер'
        for vacancy in self._get_list_of_vacancies(first + 'NOT' + second + 'NOT' + third):
            self.assertIn(first, vacancy)
            self.assertNotIn(second, vacancy)
            self.assertNotIn(third, vacancy)

    def test_boolean_equation(self):
        first, second, third, fourth = 'столяр', 'столяр-плотник', 'электрик', 'сантехник'
        search_query = '({} OR {}) AND ({} OR {})'.format(
            first, second, third, fourth
        )
        for vacancy in self._get_list_of_vacancies(search_query):
            self.assertTrue(any(item in vacancy for item in (first, second)))
            self.assertTrue(any(item in vacancy for item in (third, fourth)))

    def test_json_fields(self):
        vacancies = self._get_vacancies_json('NAME:(python OR java) and COMPANY_NAME:HeadHunter')
        for vacancy in vacancies:
            self.assertTrue(any([item in vacancy['name'].lower() for item in ('python', 'java')]))
            self.assertIn('HeadHunter', vacancy['employer']['name'])


class TestHHNegative(TestHH):
    def __init__(self, *args, **kwargs):
        super(TestHHNegative, self).__init__(*args, **kwargs)

    def test_invalid_request(self):
        vacancies = self._get_vacancies_json('запроооооооооос')
        self.assertEqual(len(vacancies), 0)


if __name__ == '__main__':
    unittest.main()
