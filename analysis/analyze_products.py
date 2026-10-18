import pandas as pd
from pathlib import Path

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

INPUT_FILE = DATA_DIR / "cleaned_products.csv"

# Load cleaned dataset
df = pd.read_csv(INPUT_FILE)

# Convert numeric columns
df["Product_Price"] = pd.to_numeric(
    df["Product_Price"], errors="coerce"
)

df["Product_Rating"] = pd.to_numeric(
    df["Product_Rating"], errors="coerce"
)

print("=" * 60)
print("PRODUCT PRICE ANALYSIS")
print("=" * 60)

# 1. Overall statistics
print("\n1. OVERALL STATISTICS")
print("Total products:", len(df))
print("Number of websites:", df["Website_Name"].nunique())
print("Average price:", round(df["Product_Price"].mean(), 2))
print("Highest price:", round(df["Product_Price"].max(), 2))
print("Lowest price:", round(df["Product_Price"].min(), 2))
print(
    "Average rating:",
    round(df["Product_Rating"].mean(), 2)
)

# 2. Website-wise analysis
print("\n2. WEBSITE-WISE ANALYSIS")

website_analysis = df.groupby("Website_Name").agg(
    Total_Products=("Product_Name", "count"),
    Average_Price=("Product_Price", "mean"),
    Minimum_Price=("Product_Price", "min"),
    Maximum_Price=("Product_Price", "max"),
    Average_Rating=("Product_Rating", "mean")
).round(2)

print(website_analysis)

# Save website analysis
website_analysis.to_csv(
    DATA_DIR / "website_analysis.csv"
)

# 3. Availability analysis
print("\n3. AVAILABILITY COUNTS")

availability_counts = (
    df["Availability"]
    .fillna("Not provided")
    .value_counts()
)

print(availability_counts)

availability_counts.to_csv(
    DATA_DIR / "availability_analysis.csv",
    header=["Count"]
)

# 4. Top 10 most expensive products
print("\n4. TOP 10 MOST EXPENSIVE PRODUCTS")

top_expensive = df.nlargest(
    10, "Product_Price"
)[["Product_Name", "Product_Price", "Website_Name"]]

print(top_expensive.to_string(index=False))

top_expensive.to_csv(
    DATA_DIR / "top_10_expensive_products.csv",
    index=False
)

print("\nAnalysis completed successfully!")
print("Results saved in the data folder.")