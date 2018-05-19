import unittest

import steamreviews


class TestSteamReviewsMethods(unittest.TestCase):

    def test_load_review_dict(self):
        app_id = 329070
        review_dict = steamreviews.load_review_dict(app_id)
        self.assertTrue('reviews' in review_dict)

    def test_download_reviews_for_app_id(self):
        app_id = 573170
        review_dict, query_count = steamreviews.download_reviews_for_app_id(app_id)
        self.assertGreater(query_count, 0)

    def test_download_reviews(self):
        app_ids = [329070, 573170]
        steamreviews.download_reviews_for_app_id_batch(app_ids)
        review_dict = steamreviews.load_review_dict(329070)
        self.assertGreater(len(review_dict['reviews']), 1)


if __name__ == '__main__':
    unittest.main()
