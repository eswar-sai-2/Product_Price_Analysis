from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import date
import re
import time


BASE_URL = "https://scrapingsandbox.com"
TABLE_URL = "https://scrapingsandbox.com/data-table"


def scrape_products():

    all_products = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Opening Scraping Sandbox...")

        page.goto(
            TABLE_URL,
            wait_until="networkidle"
        )

        # 20 pages × 25 products = 500 products
        for page_number in range(1, 21):

            print(f"\nScraping page {page_number}/20...")

            # Wait for product rows
            page.wait_for_selector("tr.product-row")

            rows = page.locator("tr.product-row")

            row_count = rows.count()

            print("Products found:", row_count)

            for i in range(row_count):

                row = rows.nth(i)

                cells = row.locator("td")

                # Skip invalid rows
                if cells.count() < 9:
                    continue

                # -------------------------
                # Product ID
                # -------------------------

                product_id = cells.nth(0).inner_text().strip()


                # -------------------------
                # Product Name + URL
                # -------------------------

                title_link = cells.nth(2).locator("a")

                product_name = title_link.inner_text().strip()

                product_url = title_link.get_attribute("href")

                if product_url:

                    if product_url.startswith("/"):
                        product_url = BASE_URL + product_url

                else:
                    product_url = ""


                # -------------------------
                # Brand / Vendor
                # -------------------------

                brand = cells.nth(3).inner_text().strip()


                # -------------------------
                # Category
                # -------------------------

                category = cells.nth(4).inner_text().strip()


                # -------------------------
                # Product Price
                # -------------------------

                price_text = cells.nth(5).inner_text().strip()

                price_text = (
                    price_text
                    .replace("$", "")
                    .replace(",", "")
                    .strip()
                )

                try:
                    product_price = float(price_text)

                except ValueError:
                    product_price = None


                # -------------------------
                # Product Rating
                # -------------------------

                rating_text = cells.nth(6).inner_text().strip()

                try:
                    product_rating = float(rating_text)

                except ValueError:
                    product_rating = None


                # -------------------------
                # Availability
                # -------------------------

                stock_text = cells.nth(7).inner_text().strip()

                if stock_text.lower() == "yes":

                    availability = "In Stock"

                elif stock_text.lower() == "no":

                    availability = "Out of Stock"

                else:

                    availability = stock_text


                # -------------------------
                # SKU
                # -------------------------

                sku = cells.nth(8).inner_text().strip()


                # -------------------------
                # Store product
                # -------------------------

                all_products.append({

                    "Product_ID": product_id,

                    "Product_Name": product_name,

                    "Product_Price": product_price,

                    "Original_Price": None,

                    "Discount": None,

                    "Product_Rating": product_rating,

                    "Number_of_Reviews": None,

                    "Brand": brand,

                    "Category": category,

                    "Availability": availability,

                    "SKU": sku,

                    "Product_URL": product_url,

                    "Website_Name": "Scraping Sandbox",

                    "Date_Scraped": date.today()
                })


            # -------------------------
            # Go to next page
            # -------------------------

            if page_number < 20:

                next_page_number = page_number + 1

                next_button = page.get_by_role(
                    "button",
                    name=str(next_page_number),
                    exact=True
                )

                next_button.click()

                page.wait_for_timeout(300)


        browser.close()


    return all_products


# ==========================================
# START SCRAPING
# ==========================================

products = scrape_products()


# ==========================================
# CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(products)


# Remove duplicate products
df = df.drop_duplicates(
    subset=["Product_ID"]
)


# ==========================================
# SAVE CSV
# ==========================================

output_file = "data/raw_products.csv"

df.to_csv(
    output_file,
    index=False
)


# ==========================================
# FINAL RESULT
# ==========================================

print("\n")
print("=" * 60)
print("SCRAPING COMPLETED")
print("=" * 60)

print("Total products scraped:", len(df))

print("CSV file:", output_file)

print("\nFirst 5 products:")
print(df.head())

print("\nColumns:")
print(df.columns.tolist())