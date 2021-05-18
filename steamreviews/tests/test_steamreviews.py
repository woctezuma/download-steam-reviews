import unittest

import steamreviews


class TestSteamReviewsMethods(unittest.TestCase):
    def test_load_review_dict(self):
        app_id = 329070
        review_dict = steamreviews.load_review_dict(app_id)
        self.assertTrue("reviews" in review_dict)

    def test_download_reviews_for_app_id(self):
        app_id = 573170
        _, query_count = steamreviews.download_reviews_for_app_id(app_id, verbose=True)
        self.assertGreater(query_count, 0)

    def test_download_reviews(self):
        app_ids = [329070, 573170]
        steamreviews.download_reviews_for_app_id_batch(app_ids, verbose=True)
        review_dict = steamreviews.load_review_dict(329070)
        self.assertGreater(len(review_dict["reviews"]), 1)

    def test_download_reviews_with_recent_filter_and_day_range(self):
        app_id = 239350
        request_params = dict()
        request_params["filter"] = "recent"
        request_params["day_range"] = "3"
        _, query_count = steamreviews.download_reviews_for_app_id(
            app_id, chosen_request_params=request_params, verbose=True
        )
        self.assertGreater(query_count, 0)

    def test_download_reviews_with_updated_filter_and_day_range(self):
        app_id = 239350
        request_params = dict()
        request_params["filter"] = "updated"
        request_params["day_range"] = "3"
        _, query_count = steamreviews.download_reviews_for_app_id(
            app_id, chosen_request_params=request_params, verbose=True
        )
        self.assertGreater(query_count, 0)


if __name__ == "__main__":
    unittest.main()
