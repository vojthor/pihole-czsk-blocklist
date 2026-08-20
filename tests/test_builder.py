import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_czsk_dns import extract_rules, normalize_domain


class BuilderTests(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(normalize_domain("Ads.Example.CZ"), "ads.example.cz")
        self.assertIsNone(normalize_domain("example"))
        self.assertIsNone(normalize_domain("127.0.0.1"))
        self.assertIsNone(normalize_domain("-invalid.example"))

    def test_extracts_only_safe_domain_wide_rules(self):
        lines = [
            "||ads.example.cz^",
            "||ads.example.cz^",
            "||tracker.example.sk^$third-party",
            "||example.cz/ads/",
            "@@||allowed.example.cz^",
            "example.cz##.advert",
            "||*.wildcard.example.cz^",
        ]
        self.assertEqual(extract_rules(lines), ["||ads.example.cz^"])


if __name__ == "__main__":
    unittest.main()
