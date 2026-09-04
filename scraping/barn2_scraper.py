from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import date
import re
import time


BASE_URL = "https://productfilters.barn2.com/"


def clean_price(price_text):
    if not price_text:
        return None

    prices = re.findall(
        r"\d+(?:\.\d+)?",
        price_text.replace(",", "")
    )

    if prices:
        return float(prices[0])

    return None


def get_rating(rating_element):
    if not rating_element:
        return None

    aria_label = rating_element.get_attribute("aria-label")

    if aria_label:
        match = re.search(
            r"(\d+(?:\.\d+)?)",
            aria_label
        )

        if match:
            return float(match.group(1))

    return None


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Opening Barn2 WooCommerce Demo...")

    page.goto(
        BASE_URL,
        wait_until="networkidle"
    )

    all_products = []

    # Scrape pages 1 to 5
    for page_number in range(1, 6):

        print(f"Scraping page {page_number}...")

        page.wait_for_selector("li.product")

        products = page.locator("li.product")

        count = products.count()

        print(f"Products found: {count}")

        for i in range(count):

            product = products.nth(i)

            # Product name
            name_element = product.locator(
                ".woocommerce-loop-product__title"
            )

            if name_element.count() == 0:
                continue

            product_name = name_element.inner_text().strip()

            # Product price
            price_element = product.locator(".price")

            if price_element.count() > 0:

                price_text = price_element.inner_text().strip()

            else:

                price_text = ""

            product_price = clean_price(price_text)

            # Product rating
            rating_element = product.locator(".star-rating")

            if rating_element.count() > 0:

                rating = get_rating(
                    rating_element.first
                )

            else:

                rating = None

            all_products.append({
                "Product_Name": product_name,
                "Product_Price": product_price,
                "Product_Rating": rating,
                "Website_Name": "Barn2",
                "Date_Scraped": str(date.today())
            })

        # Move to next page
        if page_number < 5:

            next_number = page_number + 1

            print(
                f"Clicking page {next_number}..."
            )

            next_button = page.get_by_role(
                "button",
                name=str(next_number),
                exact=True
            )

            if next_button.count() == 0:

                print(
                    f"Page {next_number} button not found."
                )

                break

            next_button.click()

            time.sleep(2)

    browser.close()


# Create DataFrame
df = pd.DataFrame(all_products)

# Remove duplicate products
df = df.drop_duplicates(
    subset=["Product_Name"]
)

# Save CSV
output_file = "data/barn2_products.csv"

df.to_csv(
    output_file,
    index=False
)


print()
print("=" * 60)
print("BARN2 SCRAPING COMPLETED")
print("=" * 60)

print(
    f"Total unique products scraped: {len(df)}"
)

print(f"CSV file: {output_file}")

print()
print("First 10 products:")

print(
    df[
        [
            "Product_Name",
            "Product_Price",
            "Product_Rating"
        ]
    ].head(10).to_string(index=False)
)