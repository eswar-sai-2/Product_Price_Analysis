from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import re

BASE_URL = "https://www.scrapingcourse.com/ecommerce/"

products = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening ScrapingCourse...")

    # There are 12 pages
    for page_number in range(1, 13):

        if page_number == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page_number}/"

        print(f"Scraping page {page_number}/12...")

        page.goto(url, wait_until="domcontentloaded")

        try:
            page.wait_for_selector("li.product", timeout=10000)
        except:
            print("No products found. Stopping.")
            break

        cards = page.locator("li.product")

        print("Products found:", cards.count())

        for i in range(cards.count()):

            card = cards.nth(i)

            # Product name
            name = card.locator(
                ".woocommerce-loop-product__title"
            ).inner_text().strip()

            # Product price
            price_text = card.locator(
                ".price"
            ).inner_text().strip()

            price_match = re.search(
                r"\d+(?:\.\d+)?",
                price_text
            )

            if price_match:
                price = float(price_match.group())
            else:
                price = None

            # Product URL
            link = card.locator("a").first.get_attribute("href")

            products.append({
                "Product_Name": name,
                "Product_Price": price,
                "Product_Rating": None,
                "Product_URL": link,
                "Website_Name": "ScrapingCourse",
                "Date_Scraped": datetime.now().strftime("%Y-%m-%d")
            })

    browser.close()


# Create DataFrame
df = pd.DataFrame(products)

# Remove duplicate products
df = df.drop_duplicates(
    subset=["Product_Name"]
)

# Create data folder
os.makedirs("data", exist_ok=True)

# Save CSV
output_file = "data/scrapingcourse_products.csv"

df.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 60)
print("SCRAPINGCOURSE SCRAPING COMPLETED")
print("=" * 60)

print("Total products scraped:", len(df))
print("CSV file:", output_file)

print("\nFirst 10 products:")

print(
    df[
        [
            "Product_Name",
            "Product_Price"
        ]
    ].head(10).to_string(index=False)
)