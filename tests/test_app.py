import tempfile
import unittest
from pathlib import Path

import pandas as pd

import app


class AppRoutesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_data_file = app.DATA_FILE
        app.DATA_FILE = Path(self.temp_dir.name) / "cleaned_products.csv"
        self.write_dataset(
            [
                {
                    "Product_Name": "Shared Hoodie",
                    "Product_Price": 42.5,
                    "Product_Rating": 4.0,
                    "Product_URL": "https://example.test/hoodie-a",
                    "Website_Name": "Source A",
                    "Date_Scraped": "2026-10-17",
                    "Availability": "In Stock",
                },
                {
                    "Product_Name": "Shared Hoodie",
                    "Product_Price": 51.0,
                    "Product_Rating": None,
                    "Product_URL": "javascript:alert(1)",
                    "Website_Name": "Source B",
                    "Date_Scraped": "2026-10-16",
                    "Availability": None,
                },
                {
                    "Product_Name": "<script>alert(1)</script>",
                    "Product_Price": 10.0,
                    "Product_Rating": 3.0,
                    "Product_URL": "https://example.test/safe",
                    "Website_Name": "Source A",
                    "Date_Scraped": "2026-10-17",
                    "Availability": "Out of Stock",
                },
            ]
        )
        app.app.config.update(TESTING=True)
        self.client = app.app.test_client()

    def tearDown(self):
        app.DATA_FILE = self.original_data_file
        self.temp_dir.cleanup()

    @staticmethod
    def write_dataset(rows):
        pd.DataFrame(rows).to_csv(app.DATA_FILE, index=False)

    def test_dashboard_calculates_metrics_and_escapes_product_names(self):
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Total products", page)
        self.assertIn(">3</strong>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("currencies not normalized", page)
        self.assertIn("Source A", page)

    def test_existing_product_route_search_filters_availability_and_paginates(self):
        response = self.client.get(
            "/products?search=hoodie&availability=In+Stock&min_rating=3"
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Shared Hoodie", page)
        self.assertIn("1 results", page)
        self.assertIn("Open source", page)
        self.assertNotIn("javascript:alert(1)", page)

    def test_valid_price_range_filters_recorded_values(self):
        response = self.client.get(
            "/products?min_price=40&max_price=45&sort_by=price_low"
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("1 results", page)
        self.assertIn("42.50", page)
        self.assertNotIn("51.00", page)

    def test_invalid_filter_values_are_reported_and_do_not_crash(self):
        response = self.client.get(
            "/products?min_price=NaN&max_price=-1&min_rating=6"
        )
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("must be a finite number", page)
        self.assertIn("must be at least 0", page)
        self.assertIn("must be no more than 5", page)

    def test_comparison_only_shows_name_candidates_with_caveat(self):
        response = self.client.get("/comparison?search=shared")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Shared Hoodie", page)
        self.assertIn("Source A", page)
        self.assertIn("Source B", page)
        self.assertIn("Candidate matches only", page)
        self.assertIn("currency metadata is absent", page.lower())
        self.assertIn("does not rank products by", page.lower())
        self.assertIn("Not rated", page)
        self.assertIn("Not provided", page)
        self.assertNotIn("javascript:alert(1)", page)

    def test_analytics_uses_existing_png_and_other_pages_render(self):
        analytics = self.client.get("/analytics")
        image = self.client.get("/visualizations/price_distribution.png")
        self.assertEqual(analytics.status_code, 200)
        self.assertIn("static PNG images, not interactive charts", analytics.get_data(as_text=True))
        self.assertEqual(image.status_code, 200)
        self.assertTrue(image.mimetype.startswith("image/"))
        image.close()
        self.assertEqual(self.client.get("/data-sources").status_code, 200)
        self.assertEqual(self.client.get("/about").status_code, 200)

    def test_data_source_counts_and_dates_are_derived_from_csv(self):
        response = self.client.get("/data-sources")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Source A", page)
        self.assertIn("2026-10-16", page)
        self.assertIn("2026-10-17", page)
        self.assertIn("Product_URL", page)

    def test_missing_dataset_returns_friendly_service_error(self):
        app.DATA_FILE = Path(self.temp_dir.name) / "missing.csv"
        response = self.client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertIn("dataset is currently unavailable", response.get_data(as_text=True))
        self.assertNotIn(self.temp_dir.name, response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
