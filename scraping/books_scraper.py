from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
import os
import re
import time

             
BASE_URL = "https://books.toscrape.com/"

                          
all_products = []

                       
def clean_price(price_text):
    if not price_text:
        return None

    match = re.search(r"\d+(?:\.\d+)?", price_text)

    if match:
        return float(match.group())

    return None


                                
def get_rating(rating_element):
    if not rating_element:
        return None

    classes = rating_element.get_attribute("class") or ""

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for word, value in rating_map.items():
        if word in classes.split():
            return value

    return None


                
with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Opening Books to Scrape...")

                                   
    for page_number in range(1, 51):

        url = urljoin(
            BASE_URL,
            f"catalogue/page-{page_number}.html"
        )

        print(f"Scraping page {page_number}/50...")

        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            if response is None or response.status >= 400:
                print("Page unavailable. Stopping.")
                break

            page.wait_for_selector(
                "article.product_pod",
                timeout=10000
            )

        except Exception as error:
            print(f"Could not load page {page_number}: {error}")
            break

                                    
        books = page.locator("article.product_pod")

        count = books.count()

        print("Books found:", count)

        if count == 0:
            print("No books found. Stopping.")
            break

                           
        for i in range(count):

            book = books.nth(i)

                       
            name_element = book.locator("h3 a")

            book_name = name_element.get_attribute("title")

            if not book_name:
                book_name = name_element.inner_text().strip()

                   
            price_text = book.locator(
                ".price_color"
            ).inner_text().strip()

            book_price = clean_price(price_text)

                    
            rating_element = book.locator(
                "p.star-rating"
            )

            if rating_element.count() > 0:
                rating = get_rating(rating_element.first)
            else:
                rating = None

                          
            availability = book.locator(
                ".availability"
            ).inner_text().strip()

                         
            relative_url = name_element.get_attribute("href")

            product_url = urljoin(url, relative_url)

                                  
            all_products.append({
                "Product_Name": book_name,
                "Product_Price": book_price,
                "Product_Rating": rating,
                "Availability": availability,
                "Product_URL": product_url,
                "Website_Name": "Books to Scrape",
                "Date_Scraped": datetime.now().strftime("%Y-%m-%d")
            })

                                  
        time.sleep(1)

    browser.close()


                                     
df = pd.DataFrame(all_products)

                               
if not df.empty:
    df = df.drop_duplicates(subset=["Product_URL"])

                      
os.makedirs("data", exist_ok=True)

          
output_file = "data/books_products.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

                 
print("\n" + "=" * 50)
print("BOOKS TO SCRAPE COMPLETED")
print("=" * 50)

print("Total books collected:", len(df))
print("CSV file:", output_file)

if not df.empty:
    print("\nFirst 10 books:")

    print(
        df[
            [
                "Product_Name",
                "Product_Price",
                "Product_Rating",
                "Availability"
            ]
        ].head(10).to_string(index=False)
    )
else:
    print("No books were collected. Check the error messages.")