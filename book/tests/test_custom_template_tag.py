import urllib

from django.test import TestCase

from django.http import HttpRequest, QueryDict

from book.templatetags.custom_template_tag import url_replace


class TestCustomTemplateTag(TestCase):

    def test_url_replace(self):

        query_key = 'search_word'
        query_val = 'Python'
        query_param = urllib.parse.urlencode({query_key: query_val})

        request = HttpRequest()
        request.method = 'GET'
        request.GET = QueryDict(query_param)

        field = 'page'
        value = 2

        get_param = url_replace(request, field, value)
        expected_get_param = urllib.parse.urlencode({query_key: query_val, field: value})

        self.assertEqual(get_param, expected_get_param)
