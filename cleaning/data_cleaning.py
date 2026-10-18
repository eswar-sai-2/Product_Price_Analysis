from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
INPUT_FILE = DATA_DIR / "all_products.csv"
OUTPUT_FILE = DATA_DIR / "cleaned_products.csv"
EXPECTED_WEBSITES = {
    "ScrapingCourse",
    "Barn2",
    "Books to Scrape",
    "Scraping Sandbox",
}


def clean_dataset(df):
    cleaned = df.copy()

    if "Website_Name" not in cleaned.columns:
        raise ValueError("Combined input is missing Website_Name")

    cleaned["Website_Name"] = (
        cleaned["Website_Name"].astype("string").str.strip()
    )
    if (
        cleaned["Website_Name"].isna().any()
        or cleaned["Website_Name"].eq("").any()
    ):
        raise ValueError("Combined input contains rows without a website name")

    present_websites = set(cleaned["Website_Name"].unique())
    missing_websites = EXPECTED_WEBSITES - present_websites
    if missing_websites:
        raise ValueError(
            f"Combined input is missing website(s): "
            f"{sorted(missing_websites)}"
        )

    text_columns = [
        "Product_Name",
        "Brand",
        "Category",
        "Availability",
        "SKU",
        "Product_URL",
        "Website_Name",
    ]

    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column].astype("string").str.strip()
            )

    if "Product_Price" in cleaned.columns:
        price = cleaned["Product_Price"].astype("string").str.replace(
            r"[^0-9.-]",
            "",
            regex=True,
        )
        cleaned["Product_Price"] = pd.to_numeric(
            price,
            errors="coerce",
        )
        cleaned.loc[
            cleaned["Product_Price"] < 0,
            "Product_Price",
        ] = pd.NA

    if "Product_Rating" in cleaned.columns:
        cleaned["Product_Rating"] = pd.to_numeric(
            cleaned["Product_Rating"],
            errors="coerce",
        )
        invalid_rating = (
            (cleaned["Product_Rating"] < 0)
            | (cleaned["Product_Rating"] > 5)
        )
        cleaned.loc[invalid_rating, "Product_Rating"] = pd.NA

    if "Number_of_Reviews" in cleaned.columns:
        cleaned["Number_of_Reviews"] = pd.to_numeric(
            cleaned["Number_of_Reviews"],
            errors="coerce",
        )

    if "Date_Scraped" in cleaned.columns:
        cleaned["Date_Scraped"] = pd.to_datetime(
            cleaned["Date_Scraped"],
            errors="coerce",
        )

    if "Availability" in cleaned.columns:
        cleaned["Availability"] = cleaned["Availability"].replace(
            {
                "yes": "In Stock",
                "Yes": "In Stock",
                "YES": "In Stock",
                "no": "Out of Stock",
                "No": "Out of Stock",
                "NO": "Out of Stock",
            }
        )

    return cleaned


def clean_combined_dataset():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Combined input not found: {INPUT_FILE}"
        )

    source = pd.read_csv(INPUT_FILE)
    if "Website_Name" not in source.columns:
        raise ValueError("Combined input is missing Website_Name")

    source_counts = (
        source["Website_Name"]
        .astype("string")
        .str.strip()
        .value_counts()
        .to_dict()
    )
    cleaned = clean_dataset(source)
    cleaned_counts = cleaned["Website_Name"].value_counts().to_dict()

    if len(cleaned) != len(source) or cleaned_counts != source_counts:
        raise RuntimeError(
            "Cleaning changed the total or per-website row counts"
        )
    if list(cleaned.columns) != list(source.columns):
        raise RuntimeError("Cleaning changed the input columns")

    cleaned.to_csv(OUTPUT_FILE, index=False)

    print("Cleaned products:", len(cleaned))
    print("Products by website:")
    print(cleaned["Website_Name"].value_counts())
    print("Saved to:", OUTPUT_FILE)

    return cleaned


if __name__ == "__main__":
    clean_combined_dataset()
