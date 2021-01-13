from django.test import TestCase, Client
from login.models import *


# Create your tests here.
class AutotestTestCase(TestCase):

    def setUp(self):
        self.c = Client()
        user = User.objects.create(username='wsq')
        user.set_password('123456')
        user.save()

    def test_login_view_get(self):
        response = self.c.get('/login/')
        status_code = response.status_code
        self.assertEquals(status_code, 200, '响应代码不为200')

    def test_login_view_post(self):
        response = self.c.post('/login/', {'username': 'wsq', 'password': '123456'}, follow=True)
        # print(response.content.decode(encoding='utf-8'))
        status_code = response.status_code
        self.assertEquals(status_code, 200, '响应代码不为200')
        self.assertTrue('Permission Denied' not in response.content.decode(encoding='utf-8'))

    def test_login(self):
        response = self.c.login(username='wsq', password='123456')
        self.assertTrue(response)
        self.c.logout()

    def test_login_fail(self):
        response = self.c.login(username='wsq', password='xxxxxx')
        self.assertFalse(response)

    def test_logout_within_login(self):
        response = self.c.logout()
        self.assertFalse(response)


