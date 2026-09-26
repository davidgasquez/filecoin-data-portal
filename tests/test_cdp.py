import datetime as dt
import unittest
from email.utils import format_datetime
from unittest.mock import call, patch

import httpx

from fdp.resources import cdp

URL = "https://cdp.allocator.tech/allocators"


def response(status, **kwargs):
    return httpx.Response(status, request=httpx.Request("GET", URL), **kwargs)


class CDPRetryTests(unittest.TestCase):
    def setUp(self):
        client = self.enterContext(patch("fdp.resources.cdp.httpx.Client"))
        self.get = client.return_value.__enter__.return_value.get
        self.sleep = self.enterContext(patch("fdp.resources.cdp.time.sleep"))
        self.enterContext(patch("fdp.resources.cdp.random.uniform", return_value=0.5))

    def test_transient_status_recovers(self):
        for status in (429, 500, 502, 503, 504):
            with self.subTest(status=status):
                self.get.reset_mock()
                self.sleep.reset_mock()
                self.get.side_effect = [
                    response(status),
                    response(200, json={"data": []}),
                ]
                self.assertEqual(cdp.get_json(URL), {"data": []})
                self.assertEqual(self.get.call_count, 2)
                self.sleep.assert_called_once_with(2.5)

    def test_transport_failure_recovers(self):
        for error in (httpx.ConnectError, httpx.ReadError, httpx.ReadTimeout):
            with self.subTest(error=error):
                self.get.side_effect = [
                    error("unavailable"),
                    response(200, json={"data": []}),
                ]
                self.assertEqual(cdp.get_json(URL), {"data": []})

    def test_persistent_failure_is_raised_after_four_attempts(self):
        for error in (response(500), httpx.ReadTimeout("unavailable")):
            with self.subTest(error=error):
                self.get.reset_mock()
                self.sleep.reset_mock()
                self.get.side_effect = [error] * 4
                with self.assertRaises((httpx.HTTPStatusError, httpx.ReadTimeout)):
                    cdp.get_json(URL)
                self.assertEqual(self.get.call_count, 4)
                self.assertEqual(
                    self.sleep.call_args_list, [call(2.5), call(4.5), call(8.5)]
                )

    def test_permanent_status_is_not_retried(self):
        for status in (400, 401, 403, 404, 501):
            with self.subTest(status=status):
                self.get.reset_mock()
                self.get.side_effect = [response(status)]
                with self.assertRaises(httpx.HTTPStatusError):
                    cdp.get_json(URL)
                self.assertEqual(self.get.call_count, 1)
        self.sleep.assert_not_called()

    def test_invalid_json_is_not_retried(self):
        self.get.side_effect = [response(200, text="not json")]
        with self.assertRaises(ValueError):
            cdp.get_json(URL)
        self.get.assert_called_once()
        self.sleep.assert_not_called()

    def test_retry_after_seconds_is_honored_and_capped(self):
        for value, expected in [
            ("20", 20),
            ("99999", 60),
            ("-1", 2.5),
            ("invalid", 2.5),
        ]:
            with self.subTest(value=value):
                self.sleep.reset_mock()
                self.get.side_effect = [
                    response(429, headers={"Retry-After": value}),
                    response(200, json={"data": []}),
                ]
                cdp.get_json(URL)
                self.sleep.assert_called_once_with(expected)

    def test_retry_after_http_date(self):
        now = dt.datetime(2026, 9, 26, tzinfo=dt.UTC)
        with patch("fdp.resources.cdp.dt") as clock:
            clock.datetime.now.return_value = now
            clock.UTC = dt.UTC
            for seconds, expected in [(30, 30), (600, 60), (-30, 2.5)]:
                header = format_datetime(
                    now + dt.timedelta(seconds=seconds), usegmt=True
                )
                self.assertEqual(
                    cdp.retry_delay(response(503, headers={"Retry-After": header}), 1),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
