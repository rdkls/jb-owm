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

    def test_get_weather_melbourne_only(self):
        res = self.app.get('/weather?q=Melbourne&api_key=%s' % API_KEY_VALID)
        self.assertEqual(200, res.status_code)

        # Ensure we only get one string, of alphanumeric chars (no json etc) back
        s = res.get_data(as_text=True)
        self.assertRegex(s, "^[\w ]+$")

    def test_get_weather_melbourne_au(self):
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        self.assertEqual(200, res.status_code)

        # Ensure we only get one string, of alphanumeric chars (no json etc) back
        s = res.get_data(as_text=True)
        self.assertRegex(s, "^[\w ]+$")

    def test_ratelimit(self):
        # Best to not assume how many requests / tests have run prior
        # Just make enough to be sure we're over the allowed number per hour
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)

        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        self.assertEqual(429, res.status_code)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        self.assertEqual(429, res.status_code)
        res = self.app.get('/weather?q=Melbourne,au&api_key=%s' % API_KEY_VALID)
        self.assertEqual(429, res.status_code)

if __name__ == '__main__':
    unittest.main()
