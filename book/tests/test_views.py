from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase


class TestBookSearchView(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user', email='test@example.com', password='password'
        )

    def test_post_search_request(self):

        response = self.client.post(reverse('book:search'), {
            'book_name': 'Python',
        })
        print(response)
        self.assertTrue(response)
