import pandas as pd
import matplotlib.pyplot as plt


# ==================================================
# LOAD CLEANED DATA
# ==================================================

df = pd.read_csv("data/cleaned_products.csv")

print("=" * 60)
print("PRODUCT PRICE ANALYSIS")
print("=" * 60)


# ==================================================
# 1. TOTAL PRODUCTS
# ==================================================

print("\nTotal Products:", len(df))


# ==================================================
# 2. WEBSITE-WISE PRODUCT COUNT
# ==================================================

print("\nProducts by Website:")
print(df["Website_Name"].value_counts())


# ==================================================
# 3. AVERAGE PRICE
# ==================================================

print("\nAverage Price:")
print(df["Product_Price"].mean())


# ==================================================
# 4. HIGHEST PRICE
# ==================================================

print("\nHighest Price:")
print(df["Product_Price"].max())


# ==================================================
# 5. LOWEST PRICE
# ==================================================

print("\nLowest Price:")
print(df["Product_Price"].min())


# ==================================================
# 6. AVERAGE RATING
# ==================================================

print("\nAverage Rating:")
print(df["Product_Rating"].mean())


# ==================================================
# 7. MOST EXPENSIVE PRODUCT
# ==================================================

most_expensive = df.loc[
    df["Product_Price"].idxmax()
]

print("\nMost Expensive Product:")
print("Name:", most_expensive["Product_Name"])
print("Price:", most_expensive["Product_Price"])
print("Website:", most_expensive["Website_Name"])


# ==================================================
# 8. CHEAPEST PRODUCT
# ==================================================

cheapest = df.loc[
    df["Product_Price"].idxmin()
]

print("\nCheapest Product:")
print("Name:", cheapest["Product_Name"])
print("Price:", cheapest["Product_Price"])
print("Website:", cheapest["Website_Name"])


# ==================================================
# 9. HIGHEST RATED PRODUCT
# ==================================================

if df["Product_Rating"].notna().any():

    highest_rated = df.loc[
        df["Product_Rating"].idxmax()
    ]

    print("\nHighest Rated Product:")
    print("Name:", highest_rated["Product_Name"])
    print("Rating:", highest_rated["Product_Rating"])
    print("Website:", highest_rated["Website_Name"])

else:

    print("\nHighest Rated Product:")
    print("Rating data is not available.")


# ==================================================
# 10. WEBSITE-WISE AVERAGE PRICE
# ==================================================

print("\nAverage Price by Website:")

website_price = df.groupby(
    "Website_Name"
)["Product_Price"].mean()

print(website_price)


# ==================================================
# 11. WEBSITE-WISE AVERAGE RATING
# ==================================================

print("\nAverage Rating by Website:")

website_rating = df.groupby(
    "Website_Name"
)["Product_Rating"].mean()

print(website_rating)


# ==================================================
# 12. PRICE COMPARISON BY WEBSITE
# ==================================================

plt.figure(figsize=(8, 6))

website_price.plot(kind="bar")

plt.title("Average Product Price by Website")
plt.xlabel("Website")
plt.ylabel("Average Price")

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "charts/website_price_comparison.png"
)

plt.show()


# ==================================================
# 13. PRICE DISTRIBUTION
# ==================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["Product_Price"],
    bins=10
)

plt.title("Product Price Distribution")
plt.xlabel("Product Price")
plt.ylabel("Number of Products")

plt.tight_layout()

plt.savefig(
    "charts/price_distribution.png"
)

plt.show()


# ==================================================
# 14. RATING DISTRIBUTION
# ==================================================

rating_data = df["Product_Rating"].dropna()

if len(rating_data) > 0:

    rating_counts = rating_data.value_counts().sort_index()

    plt.figure(figsize=(10, 6))

    rating_counts.plot(kind="bar")

    plt.title("Product Rating Distribution")
    plt.xlabel("Product Rating")
    plt.ylabel("Number of Products")

    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        "charts/rating_distribution.png"
    )

    plt.show()


# ==================================================
# 15. RATING VS PRICE
# ==================================================

rating_price = df.dropna(
    subset=[
        "Product_Price",
        "Product_Rating"
    ]
)

if len(rating_price) > 0:

    plt.figure(figsize=(10, 6))

    plt.scatter(
        rating_price["Product_Price"],
        rating_price["Product_Rating"]
    )

    plt.title("Price vs Product Rating")
    plt.xlabel("Product Price")
    plt.ylabel("Product Rating")

    plt.tight_layout()

    plt.savefig(
        "charts/rating_vs_price.png"
    )

    plt.show()


# ==================================================
# FINAL
# ==================================================

print("\n" + "=" * 60)
print("ANALYSIS COMPLETED")
print("=" * 60)