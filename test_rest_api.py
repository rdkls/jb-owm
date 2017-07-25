#!/usr/bin/env python
import unittest
import rest_api
import logging

API_KEY_VALID   = 'd15338c1e1080b032301667d07460fec'
API_KEY_INVALID = 'xxx'

class TestRestAPI(unittest.TestCase):
    def setUp(self):
        rest_api.app.testing = True
        self.app = rest_api.app.test_client()

    def test_get_weather_bad_apikey(self):
        res = self.app.get('/weather?api_key=%s' % API_KEY_INVALID)
        self.assertEqual(401, res.status_code)

    def test_get_weather_no_apikey(self):
        res = self.app.get('/weather')
        self.assertEqual(401, res.status_code)

    def test_get_weather_no_q(self):
        res = self.app.get('/weather?api_key=%s' % API_KEY_VALID)
        self.assertEqual(400, res.status_code)

    def test_get_weather_bad_q(self):
        res = self.app.get('/weather?api_key=%s&q=' % API_KEY_VALID)
        self.assertEqual(400, res.status_code)

    def test_get_weather(self):
        res = self.app.get('/weather')
        #logging.error(res.response)
        #logging.error(res.status_code)
        self.assertEqual(401, res.status_code)

    def test_iget_weather(self):
        #self.assertTrue(False)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
