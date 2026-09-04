import pandas as pd


# Load both website datasets
website1 = pd.read_csv("data/scrapingcourse_products.csv")
website2 = pd.read_csv("data/barn2_products.csv")


# Convert product names to lowercase for matching
website1["Match_Name"] = website1["Product_Name"].str.lower().str.strip()
website2["Match_Name"] = website2["Product_Name"].str.lower().str.strip()


# Find products available on both websites
comparison = pd.merge(
    website1,
    website2,
    on="Match_Name",
    suffixes=("_Website1", "_Website2")
)


# Calculate price difference
comparison["Price_Difference"] = (
    comparison["Product_Price_Website1"]
    - comparison["Product_Price_Website2"]
)


# Find cheaper website
comparison["Cheaper_Website"] = comparison.apply(
    lambda row:
        "ScrapingCourse"
        if row["Price_Difference"] < 0
        else
        "Barn2"
        if row["Price_Difference"] > 0
        else
        "Same Price",
    axis=1
)


print("=" * 70)
print("SAME PRODUCT - DIFFERENT WEBSITE COMPARISON")
print("=" * 70)

print("\nMatching products found:", len(comparison))


# Display comparison
print("\nPRICE COMPARISON")
print("-" * 70)

for _, row in comparison.iterrows():

    print("\nProduct:", row["Product_Name_Website1"])

    print(
        "ScrapingCourse Price: $",
        row["Product_Price_Website1"]
    )

    print(
        "Barn2 Price: $",
        row["Product_Price_Website2"]
    )

    print(
        "Price Difference: $",
        abs(row["Price_Difference"])
    )

    print(
        "Cheaper Website:",
        row["Cheaper_Website"]
    )


# Save comparison result
comparison.to_csv(
    "data/product_comparison.csv",
    index=False
)


# --------------------------------------------------
# RECOMMENDATION
# --------------------------------------------------

print("\n" + "=" * 70)
print("PRODUCT RECOMMENDATIONS")
print("=" * 70)

for _, row in comparison.iterrows():

    product = row["Product_Name_Website1"]

    if row["Cheaper_Website"] == "Same Price":

        print(
            f"{product}: Both websites have the same price."
        )

    else:

        print(
            f"{product}: Buy from {row['Cheaper_Website']} "
            f"to save ${abs(row['Price_Difference']):.2f}."
        )


print("\nComparison file saved:")
print("data/product_comparison.csv")