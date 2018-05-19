import unittest

import steamreviews


class TestSteamReviewsMethods(unittest.TestCase):

    def test_load_review_dict(self):
        review_dict = steamreviews.load_review_dict(329070)
        self.assertDictEqual(review_dict, {'reviews': {}})

    def test_download_reviews_for_app_id(self):
        review_dict, query_count = steamreviews.download_reviews_for_app_id(573170)
        self.assertGreater(query_count, 0)

    def test_download_reviews(self):
        self.assertTrue(steamreviews.download_reviews([329070, 573170]))


if __name__ == '__main__':
    unittest.main()
