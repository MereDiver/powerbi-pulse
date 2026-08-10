import os
import sys
import types
import unittest
from unittest.mock import patch

import proxy_support


class ProxySupportTests(unittest.TestCase):
    def tearDown(self):
        proxy_support.restore_proxy_environment()

    def test_authenticated_http_status_still_proves_transport(self):
        fake_pypac = types.ModuleType("pypac")
        fake_pypac.get_pac = lambda: object()
        fake_resolver_module = types.ModuleType("pypac.resolver")

        class FakeResolver:
            def __init__(self, _pac):
                pass

            def get_proxy_for_requests(self, _url):
                return {"https": "http://proxy.example:8080"}

        fake_resolver_module.ProxyResolver = FakeResolver
        response = types.SimpleNamespace(status_code=401)

        with patch.dict(
            sys.modules,
            {"pypac": fake_pypac, "pypac.resolver": fake_resolver_module},
        ), patch.object(proxy_support.requests, "get", return_value=response), patch.dict(
            os.environ, {"HTTPS_PROXY": "http://original.example:8080"}, clear=False
        ):
            proxies = proxy_support.configure_pac_proxy()
            self.assertEqual(proxies["https"], "http://proxy.example:8080")
            self.assertEqual(os.environ["HTTPS_PROXY"], "http://proxy.example:8080")
            proxy_support.restore_proxy_environment()
            self.assertEqual(os.environ["HTTPS_PROXY"], "http://original.example:8080")


if __name__ == "__main__":
    unittest.main()

