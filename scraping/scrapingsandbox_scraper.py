import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from playwright.sync_api import sync_playwright

                                                              
               
                                                              

BASE_URL = "https://scrapingsandbox.com/"
OUTPUT_FILE = "data/scrapingsandbox_products.csv"
WEBSITE_NAME = "Scraping Sandbox"
MAX_PAGES = 30
PAGE_WAIT_MS = 900

CARD_SELECTORS = [".product-card", "[data-product-id]", "article"]
TITLE_SELECTORS = [
    ".product-title",
    "[class*='product-name' i]",
    "[class*='product-title' i]",
    "h1", "h2", "h3", "h4",
]
PRICE_SELECTORS = [
    ".product-price",
    "[class*='product-price' i]",
    "[class*='price' i]",
    "[data-price]",
]
RATING_SELECTORS = [
    ".product-rating",
    "[class*='rating' i]",
    "[aria-label*='rating' i]",
    "[title*='rating' i]",
]


                                                              
         
                                                              

def safe_text(locator):
    try:
        return locator.inner_text().strip()
    except Exception:
        return ""


def safe_attr(locator, name):
    try:
        return locator.get_attribute(name) or ""
    except Exception:
        return ""


def number_from(text):
    if not text:
        return None
    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(text))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except (ValueError, TypeError):
        return None


def get_cards(page):
    for selector in CARD_SELECTORS:
        try:
            cards = page.locator(selector)
            if cards.count() > 0:
                return cards
        except Exception:
            pass
    return page.locator(".product-card")


def first_nonempty(card, selectors):
    for selector in selectors:
        try:
            items = card.locator(selector)
            for i in range(items.count()):
                item = items.nth(i)
                text = safe_text(item)
                if text:
                    return item
        except Exception:
            pass
    return None


                                                              
                  
                                                              

def extract_name(card, card_text):
    element = first_nonempty(card, TITLE_SELECTORS)
    if element is not None:
        name = safe_text(element)
        if not name:
            name = (
                safe_attr(element, "title")
                or safe_attr(element, "aria-label")
                or safe_attr(element, "alt")
            ).strip()
        if name and not re.search(
            r"^\$?\s*\d[\d,.]*$|in stock|out of stock|add to cart",
            name, re.I
        ):
            return name

                                                                     
    lines = [re.sub(r"\s+", " ", x).strip()
             for x in card_text.splitlines() if x.strip()]
    for line in lines:
        if re.search(r"SKU[-\s:]|in stock|out of stock|add to cart", line, re.I):
            continue
        if re.search(r"[$₹€£]\s*\d", line):
            continue
        if re.fullmatch(r"\d+(?:\.\d+)?", line):
            continue
        if re.fullmatch(
            r"health|electronics|food\s*&\s*beverage|automotive|art|"
            r"pet supplies|toys|music|books|jewelry|office supplies",
            line, re.I
        ):
            continue
        return line
    return ""


def extract_price(card, card_text):
    for selector in PRICE_SELECTORS:
        try:
            items = card.locator(selector)
            for i in range(items.count()):
                item = items.nth(i)
                text = (
                    safe_text(item)
                    or safe_attr(item, "content")
                    or safe_attr(item, "data-price")
                    or safe_attr(item, "aria-label")
                )
                value = number_from(text)
                if value is not None and re.search(
                    r"[$₹€£]|\b(price|cost)\b", text, re.I
                ):
                    return value
        except Exception:
            pass

                                                                               
    matches = re.findall(r"[$₹€£]\s*(\d[\d,]*(?:\.\d{1,2})?)", card_text)
    if matches:
        try:
            return float(matches[0].replace(",", ""))
        except ValueError:
            pass

    for line in card_text.splitlines():
        if re.search(r"\b(price|cost)\b", line, re.I):
            value = number_from(line)
            if value is not None:
                return value
    return None


def extract_rating(card, card_text):
    for selector in RATING_SELECTORS:
        try:
            items = card.locator(selector)
            for i in range(items.count()):
                item = items.nth(i)
                text = (
                    safe_attr(item, "aria-label")
                    or safe_attr(item, "title")
                    or safe_text(item)
                )
                value = number_from(text)
                if value is not None and 0 <= value <= 5:
                    return value
        except Exception:
            pass

                                                                     
                                                                 
    lines = [x.strip() for x in card_text.splitlines() if x.strip()]
    for line in lines:
        if re.search(r"SKU|[$₹€£]|stock", line, re.I):
            continue
        if re.fullmatch(r"\d(?:\.\d)?", line):
            value = float(line)
            if 0 <= value <= 5:
                return value
    match = re.search(r"(\d(?:\.\d+)?)\s*(?:/5|out of 5|stars?)", card_text, re.I)
    if match:
        value = float(match.group(1))
        if 0 <= value <= 5:
            return value
    return None


def extract_url(card):
    try:
        href = card.evaluate("""el => {
            if (el.matches('a[href]')) return el.getAttribute('href');
            const a = el.querySelector('a[href]');
            if (a) return a.getAttribute('href');
            return el.getAttribute('data-href') ||
                   el.getAttribute('data-url') || '';
        }""")
        if href and not href.strip().lower().startswith(("javascript:", "mailto:", "tel:")):
            return urljoin(BASE_URL, href.strip())
    except Exception:
        pass
    return ""


def extract_product(card):
    card_text = safe_text(card)
    name = extract_name(card, card_text)
    if not name:
        return None

    if re.search(r"\bout of stock\b", card_text, re.I):
        availability = "Out of Stock"
    elif re.search(r"\bin stock\b", card_text, re.I):
        availability = "In Stock"
    elif re.search(r"\bavailable\b", card_text, re.I):
        availability = "Available"
    else:
        availability = ""

    return {
        "Product_Name": name,
        "Product_Price": extract_price(card, card_text),
        "Product_Rating": extract_rating(card, card_text),
        "Availability": availability,
        "Product_URL": extract_url(card),
        "Website_Name": WEBSITE_NAME,
        "Date_Scraped": datetime.now().strftime("%Y-%m-%d"),
    }


                                                              
            
                                                              

def page_signature(page):
    """Return product URLs/text for the first few visible product cards."""
    cards = get_cards(page)
    bits = []
    try:
        for i in range(min(3, cards.count())):
            card = cards.nth(i)
            href = extract_url(card)
            text = safe_text(card)
            bits.append(href or text)
    except Exception:
        pass
    return "||".join(bits)


def click_numbered_page(page, page_number):
    """
    The site's pagination is made of JavaScript buttons labelled 1, 2, 3, …, 21.
    Try a real Playwright click first, then a DOM click fallback. Confirm the cards
    actually change before reporting success.
    """
    target = str(page_number)
    old_signature = page_signature(page)
    old_url = page.url

                                                                                
    try:
        candidates = page.locator("button").filter(has_text=re.compile(rf"^\s*{re.escape(target)}\s*$"))
        for i in range(candidates.count()):
            button = candidates.nth(i)
            try:
                if not button.is_visible() or button.is_disabled():
                    continue
                if safe_text(button) != target:
                    continue

                button.click(timeout=5000, force=True)
                page.wait_for_timeout(PAGE_WAIT_MS)

                if page_signature(page) != old_signature or page.url != old_url:
                    print(f"Pagination: moved to page {page_number} by button click.")
                    return True
            except Exception as exc:
                print(f"Playwright click attempt for page {target} failed: {exc}")
    except Exception:
        pass

                                                                                     
    try:
        clicked = page.evaluate("""target => {
            const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
            const buttons = Array.from(document.querySelectorAll('button'))
                .filter(el => visible(el) && el.innerText.trim() === target);

            // Prefer buttons located inside a pagination/nav container.
            buttons.sort((a, b) => {
                const score = el => {
                    const parent = el.closest('nav, [class*="pagination" i], [aria-label*="pagination" i]');
                    return parent ? 1 : 0;
                };
                return score(b) - score(a);
            });

            const button = buttons[0];
            if (!button || button.disabled) return false;
            button.click();
            return true;
        }""", target)

        if clicked:
            for _ in range(20):
                page.wait_for_timeout(250)
                if page_signature(page) != old_signature or page.url != old_url:
                    print(f"Pagination: moved to page {page_number} by DOM click.")
                    return True
    except Exception as exc:
        print(f"DOM click attempt for page {target} failed: {exc}")

                                                                 
    try:
        info = page.locator("button").evaluate_all("""els => els.map(el => ({
            text: el.innerText.trim(),
            disabled: el.disabled,
            className: String(el.className),
            ariaCurrent: el.getAttribute('aria-current'),
            html: el.outerHTML
        })).filter(x => x.text && (/^\\d+$/.test(x.text) || x.text.includes('…') || x.text.includes('...')))""")
        print("Pagination button diagnostics:", info)
    except Exception:
        pass

    return False


                                                              
      
                                                              

def main():
    os.makedirs("data", exist_ok=True)
    products_by_key = {}

    print("=" * 65)
    print("SCRAPING SANDBOX PRODUCT SCRAPER")
    print("=" * 65)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            print("Opening website:", BASE_URL)
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1500)

            print("Page title:", page.title())
            print("Starting URL:", page.url)

            if response and response.status >= 400:
                raise RuntimeError(f"Website returned HTTP {response.status}")

            if get_cards(page).count() == 0:
                print("ERROR: No product cards were found. The page selectors may have changed.")
                return

            for page_number in range(1, MAX_PAGES + 1):
                cards = get_cards(page)
                count = cards.count()
                print("\n" + "=" * 65)
                print(f"PAGE {page_number}: {count} product cards visible")
                print("=" * 65)

                before = len(products_by_key)
                for i in range(count):
                    try:
                        product = extract_product(cards.nth(i))
                        if not product:
                            print(f"Skipping card {i + 1}: product name not found.")
                            continue

                        key = (
                            product["Product_URL"].strip().casefold()
                            if product["Product_URL"]
                            else product["Product_Name"].strip().casefold()
                        )
                        if key not in products_by_key:
                            products_by_key[key] = product
                            print(
                                f"Collected: {product['Product_Name']} | "
                                f"Price: {product['Product_Price']} | "
                                f"Rating: {product['Product_Rating']}"
                            )
                    except Exception as exc:
                        print(f"Error extracting card {i + 1}: {exc}")

                print("New unique products this page:", len(products_by_key) - before)
                print("Total unique products so far:", len(products_by_key))

                if page_number >= MAX_PAGES:
                    print("Reached MAX_PAGES limit.")
                    break

                if not click_numbered_page(page, page_number + 1):
                    print(f"Could not move to page {page_number + 1}; stopping.")
                    break

                time.sleep(0.25)

        except Exception as exc:
            print("SCRAPING ERROR:", repr(exc))
        finally:
            browser.close()

    columns = [
        "Product_Name", "Product_Price", "Product_Rating", "Availability",
        "Product_URL", "Website_Name", "Date_Scraped",
    ]
    df = pd.DataFrame(list(products_by_key.values()), columns=columns)

    if not df.empty:
        df["Product_Name"] = df["Product_Name"].astype(str).str.strip()
        df = df.drop_duplicates(subset=["Product_Name"], keep="first")
        df["Product_Price"] = pd.to_numeric(df["Product_Price"], errors="coerce")
        df["Product_Rating"] = pd.to_numeric(df["Product_Rating"], errors="coerce")
        df.loc[~df["Product_Rating"].between(0, 5), "Product_Rating"] = None
        df = df.reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print("\n" + "=" * 65)
    print("SCRAPING COMPLETED")
    print("=" * 65)
    print("Website:", WEBSITE_NAME)
    print("Unique products collected:", len(df))
    print("Products with prices:", int(df["Product_Price"].notna().sum()) if not df.empty else 0)
    print("Products with ratings:", int(df["Product_Rating"].notna().sum()) if not df.empty else 0)
    print("Products with URLs:", int(df["Product_URL"].fillna("").astype(str).str.strip().ne("").sum()) if not df.empty else 0)
    print("Products with availability:", int(df["Availability"].fillna("").astype(str).str.strip().ne("").sum()) if not df.empty else 0)
    print("CSV saved to:", OUTPUT_FILE)

    if not df.empty:
        print("\nPRICE SUMMARY")
        valid_prices = df["Product_Price"].dropna()
        if not valid_prices.empty:
            print("Average price:", round(valid_prices.mean(), 2))
            print("Minimum price:", round(valid_prices.min(), 2))
            print("Maximum price:", round(valid_prices.max(), 2))

        valid_ratings = df["Product_Rating"].dropna()
        if not valid_ratings.empty:
            print("Average rating:", round(valid_ratings.mean(), 2))

        print("\nFIRST 10 PRODUCTS")
        print(df.head(10).to_string(index=False))
    else:
        print("No products were collected. Inspect the error/diagnostic output above.")


if __name__ == "__main__":
    main()