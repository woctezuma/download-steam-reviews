import unittest

import download_reviews


class TestDownloadReviewsMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(download_reviews.main())


if __name__ == '__main__':
    unittest.main()
