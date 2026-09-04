import pandas as pd


# ==================================================
# 1. LOAD BOTH WEBSITE DATASETS
# ==================================================

website1 = pd.read_csv("data/scrapingcourse_products.csv")
website2 = pd.read_csv("data/barn2_products.csv")

print("=" * 60)
print("DATA CLEANING")
print("=" * 60)

print("\nScrapingCourse products:", len(website1))
print("Barn2 products:", len(website2))


# ==================================================
# 2. CLEAN EACH DATASET
# ==================================================

def clean_dataset(df, website_name):

    df = df.copy()

    # Add website name if it does not exist
    if "Website_Name" not in df.columns:
        df["Website_Name"] = website_name

    # Clean text columns
    text_columns = [
        "Product_Name",
        "Brand",
        "Category",
        "Availability",
        "SKU",
        "Product_URL",
        "Website_Name"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # Convert price to numeric
    if "Product_Price" in df.columns:

        df["Product_Price"] = (
            df["Product_Price"]
            .astype(str)
            .str.replace(r"[^0-9.]", "", regex=True)
        )

        df["Product_Price"] = pd.to_numeric(
            df["Product_Price"],
            errors="coerce"
        )

        # Remove invalid negative prices
        df.loc[
            df["Product_Price"] < 0,
            "Product_Price"
        ] = pd.NA

    # Convert rating to numeric
    if "Product_Rating" in df.columns:

        df["Product_Rating"] = pd.to_numeric(
            df["Product_Rating"],
            errors="coerce"
        )

        # Keep ratings only between 0 and 5
        df.loc[
            (df["Product_Rating"] < 0) |
            (df["Product_Rating"] > 5),
            "Product_Rating"
        ] = pd.NA

    # Convert review count if available
    if "Number_of_Reviews" in df.columns:

        df["Number_of_Reviews"] = pd.to_numeric(
            df["Number_of_Reviews"],
            errors="coerce"
        )

    # Convert date if available
    if "Date_Scraped" in df.columns:

        df["Date_Scraped"] = pd.to_datetime(
            df["Date_Scraped"],
            errors="coerce"
        )

    # Normalize availability
    if "Availability" in df.columns:

        df["Availability"] = df["Availability"].replace(
            {
                "yes": "In Stock",
                "Yes": "In Stock",
                "YES": "In Stock",
                "no": "Out of Stock",
                "No": "Out of Stock",
                "NO": "Out of Stock"
            }
        )

    # Remove duplicate products
    if "Product_Name" in df.columns:

        before = len(df)

        df = df.drop_duplicates(
            subset=["Product_Name"]
        )

        after = len(df)

        print(
            f"{website_name} duplicates removed:",
            before - after
        )

    return df


# ==================================================
# 3. CLEAN BOTH DATASETS
# ==================================================

website1_cleaned = clean_dataset(
    website1,
    "ScrapingCourse"
)

website2_cleaned = clean_dataset(
    website2,
    "Barn2"
)


# ==================================================
# 4. DISPLAY MISSING VALUES
# ==================================================

print("\nMissing values - ScrapingCourse:")
print(website1_cleaned.isnull().sum())

print("\nMissing values - Barn2:")
print(website2_cleaned.isnull().sum())


# ==================================================
# 5. SAVE CLEANED DATASETS
# ==================================================

website1_cleaned.to_csv(
    "data/cleaned_scrapingcourse.csv",
    index=False
)

website2_cleaned.to_csv(
    "data/cleaned_barn2.csv",
    index=False
)


# ==================================================
# 6. CREATE COMBINED DATASET
# ==================================================

combined = pd.concat(
    [
        website1_cleaned,
        website2_cleaned
    ],
    ignore_index=True
)


combined.to_csv(
    "data/cleaned_products.csv",
    index=False
)


# ==================================================
# 7. FINAL INFORMATION
# ==================================================

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED")
print("=" * 60)

print("\nScrapingCourse cleaned products:",
      len(website1_cleaned))

print("Barn2 cleaned products:",
      len(website2_cleaned))

print("Combined products:",
      len(combined))

print("\nFiles created:")

print("data/cleaned_scrapingcourse.csv")
print("data/cleaned_barn2.csv")
print("data/cleaned_products.csv")

print("\nCombined dataset columns:")
print(combined.columns.tolist())