import json
from django.test import Client, RequestFactory, TestCase
from .http import json_error, json_ok, parse_json


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_returns_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": {"status": "ok"}})


class HttpHelpersTests(TestCase):
    def test_json_ok_default(self):
        res = json_ok()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode("utf-8")), {"data": {}})

    def test_json_ok_with_data(self):
        res = json_ok({"status": "ok"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode("utf-8")), {"data": {"status": "ok"}})

    def test_json_error(self):
        res = json_error("Validation error", errors={"field": ["Required"]}, status=422)
        self.assertEqual(res.status_code, 422)
        data = json.loads(res.content.decode("utf-8"))
        self.assertEqual(data["message"], "Validation error")
        self.assertEqual(data["errors"], {"field": ["Required"]})

    def test_parse_json_valid(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data='{"key": "value"}', content_type="application/json")
        self.assertEqual(parse_json(req), {"key": "value"})

    def test_parse_json_empty(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data="", content_type="application/json")
        self.assertEqual(parse_json(req), {})

    def test_parse_json_invalid(self):
        factory = RequestFactory()
        req = factory.post("/api/test/", data="invalid-json", content_type="application/json")
        with self.assertRaises(ValueError):
            parse_json(req)
