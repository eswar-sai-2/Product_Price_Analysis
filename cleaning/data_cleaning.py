import pandas as pd


# ==========================================
# 1. READ RAW DATA
# ==========================================

input_file = "data/raw_products.csv"

df = pd.read_csv(input_file)

print("Raw data loaded successfully!")
print("Rows:", len(df))


# ==========================================
# 2. REMOVE DUPLICATE PRODUCTS
# ==========================================

before = len(df)

df = df.drop_duplicates(
    subset=["Product_ID"]
)

after = len(df)

print("Duplicates removed:", before - after)


# ==========================================
# 3. CLEAN TEXT COLUMNS
# ==========================================

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

    df[column] = df[column].astype(str).str.strip()


# ==========================================
# 4. CONVERT NUMERIC COLUMNS
# ==========================================

numeric_columns = [
    "Product_ID",
    "Product_Price",
    "Original_Price",
    "Discount",
    "Product_Rating",
    "Number_of_Reviews"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==========================================
# 5. CONVERT DATE COLUMN
# ==========================================

df["Date_Scraped"] = pd.to_datetime(
    df["Date_Scraped"],
    errors="coerce"
)


# ==========================================
# 6. CHECK INVALID PRICES
# ==========================================

df.loc[
    df["Product_Price"] < 0,
    "Product_Price"
] = pd.NA


df.loc[
    df["Original_Price"] < 0,
    "Original_Price"
] = pd.NA


# ==========================================
# 7. CHECK RATING RANGE
# ==========================================

df.loc[
    (df["Product_Rating"] < 0) |
    (df["Product_Rating"] > 5),
    "Product_Rating"
] = pd.NA


# ==========================================
# 8. CHECK AVAILABILITY
# ==========================================

df["Availability"] = df["Availability"].replace(
    {
        "yes": "In Stock",
        "Yes": "In Stock",
        "no": "Out of Stock",
        "No": "Out of Stock"
    }
)


# ==========================================
# 9. CHECK MISSING VALUES
# ==========================================

print("\nMissing values after cleaning:")

print(df.isnull().sum())


# ==========================================
# 10. SAVE CLEANED DATA
# ==========================================

output_file = "data/cleaned_products.csv"

df.to_csv(
    output_file,
    index=False
)


# ==========================================
# 11. FINAL INFORMATION
# ==========================================

print("\n" + "=" * 50)
print("DATA CLEANING COMPLETED")
print("=" * 50)

print("Total products:", len(df))

print("Cleaned file:", output_file)

print("\nData types:")

print(df.dtypes)

print("\nFirst 5 rows:")

print(df.head())