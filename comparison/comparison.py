import pandas as pd


# ==================================================
# 1. LOAD CLEANED WEBSITE DATASETS
# ==================================================

website1 = pd.read_csv("data/cleaned_scrapingcourse.csv")
website2 = pd.read_csv("data/cleaned_barn2.csv")


# ==================================================
# 2. PREPARE PRODUCT NAMES FOR MATCHING
# ==================================================

website1["Match_Name"] = (
    website1["Product_Name"]
    .str.lower()
    .str.strip()
)

website2["Match_Name"] = (
    website2["Product_Name"]
    .str.lower()
    .str.strip()
)


# ==================================================
# 3. FIND PRODUCTS AVAILABLE ON BOTH WEBSITES
# ==================================================

comparison = pd.merge(
    website1,
    website2,
    on="Match_Name",
    suffixes=("_Website1", "_Website2")
)


# ==================================================
# 4. CALCULATE PRICE DIFFERENCE
# ==================================================

comparison["Price_Difference"] = (
    comparison["Product_Price_Website1"]
    - comparison["Product_Price_Website2"]
)


# ==================================================
# 5. FIND CHEAPER WEBSITE
# ==================================================

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


# ==================================================
# 6. DISPLAY COMPARISON
# ==================================================

print("=" * 70)
print("SAME PRODUCT - DIFFERENT WEBSITE COMPARISON")
print("=" * 70)

print("\nMatching products found:", len(comparison))


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


# ==================================================
# 7. SAVE COMPARISON RESULT
# ==================================================

comparison.to_csv(
    "data/product_comparison.csv",
    index=False
)


# ==================================================
# 8. PRODUCT RECOMMENDATIONS
# ==================================================

print("\n" + "=" * 70)
print("PRODUCT RECOMMENDATIONS")
print("=" * 70)


for _, row in comparison.iterrows():

    product = row["Product_Name_Website1"]

    price1 = row["Product_Price_Website1"]
    price2 = row["Product_Price_Website2"]

    rating1 = row.get("Product_Rating_Website1")
    rating2 = row.get("Product_Rating_Website2")


    # --------------------------------------------------
    # If ratings are available on both websites
    # --------------------------------------------------

    if pd.notna(rating1) and pd.notna(rating2):

        if rating1 > rating2:

            recommended = "ScrapingCourse"
            reason = "higher rating"

        elif rating2 > rating1:

            recommended = "Barn2"
            reason = "higher rating"

        else:

            if price1 < price2:

                recommended = "ScrapingCourse"
                reason = "same rating and lower price"

            elif price2 < price1:

                recommended = "Barn2"
                reason = "same rating and lower price"

            else:

                recommended = "Both websites"
                reason = "same rating and same price"


        print(
            f"{product}: Buy from {recommended} "
            f"because it has {reason}."
        )


    # --------------------------------------------------
    # If rating is missing
    # --------------------------------------------------

    else:

        if price1 < price2:

            print(
                f"{product}: Buy from ScrapingCourse "
                f"to save ${abs(price1 - price2):.2f}."
            )

        elif price2 < price1:

            print(
                f"{product}: Buy from Barn2 "
                f"to save ${abs(price1 - price2):.2f}."
            )

        else:

            print(
                f"{product}: Both websites have the same price."
            )


# ==================================================
# 9. FINAL MESSAGE
# ==================================================

print("\nComparison file saved:")
print("data/product_comparison.csv")

print("\n" + "=" * 70)
print("COMPARISON AND RECOMMENDATION COMPLETED")
print("=" * 70)