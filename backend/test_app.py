import unittest
from predict import predict_url

class TestPhishingPrediction(unittest.TestCase):

    def test_safe_url(self):
        url = "https://www.google.com"
        result = predict_url(url)
        self.assertEqual(result, 0, f"Expected safe URL to be 0, got {result}")

    def test_phishing_url(self):
        url = "http://free-login-paypal.com"
        result = predict_url(url)
        self.assertEqual(result, 1, f"Expected phishing URL to be 1, got {result}")

    def test_empty_url(self):
        url = ""
        with self.assertRaises(Exception):
            predict_url(url)

    def test_url_with_protocol_and_www(self):
        url = "https://www.paypal-update-secure.com"
        result = predict_url(url)
        self.assertIn(result, [0, 1])  # Just checks it runs

if __name__ == '__main__':
    unittest.main()