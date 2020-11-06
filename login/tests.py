from django.test import TestCase, Client
from .models import *


# Create your tests here.
class AutotestTestCase(TestCase):

    def setUp(self):
        self.c = Client()

    def test_run_his_view(self):
        response = self.c.get('/login/')
        status_code = response.status_code
        self.assertEquals(status_code, 200, '响应代码不为200')

    def test_login(self):
        user = User.objects.create(username='wsq')
        user.set_password('123456')
        user.save()
        response = self.c.login(username='wsq', password='123456')
        self.assertTrue(response)
        self.c.logout()

    def test_login_fail(self):
        response = self.c.login(username='wsq', password='xxxxxx')
        self.assertFalse(response)

