import asyncio
import unittest
from unittest.mock import patch

import backend.main as main_module


class FinnhubRouteTests(unittest.TestCase):
    def test_finnhub_test_returns_payload_when_request_succeeds(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"c": 123.45}'

        with patch.object(main_module, "FINNHUB_API_KEY", "dummy-key"), patch.object(
            main_module, "urlopen", return_value=FakeResponse()
        ):
            response = asyncio.run(main_module.finnhub_test())

        self.assertEqual(response, {"c": 123.45})


if __name__ == "__main__":
    unittest.main()
