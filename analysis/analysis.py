import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned dataset
df = pd.read_csv("data/cleaned_products.csv")

print("=" * 50)
print("PRODUCT PRICE ANALYSIS")
print("=" * 50)

# 1. Total number of products
print("\nTotal Products:", len(df))

# 2. Average product price
print("Average Price:", df["Product_Price"].mean())

# 3. Highest product price
print("Highest Price:", df["Product_Price"].max())

# 4. Lowest product price
print("Lowest Price:", df["Product_Price"].min())

# 5. Average product rating
print("Average Rating:", df["Product_Rating"].mean())

# 6. Number of products in each category
print("\nProducts by Category:")
print(df["Category"].value_counts())

# 7. Number of products by brand
print("\nProducts by Brand:")
print(df["Brand"].value_counts())

# 8. Availability
print("\nProduct Availability:")
print(df["Availability"].value_counts())

# 9. Most expensive product
most_expensive = df.loc[df["Product_Price"].idxmax()]

print("\nMost Expensive Product:")
print("Name:", most_expensive["Product_Name"])
print("Price:", most_expensive["Product_Price"])

# 10. Cheapest product
cheapest = df.loc[df["Product_Price"].idxmin()]

print("\nCheapest Product:")
print("Name:", cheapest["Product_Name"])
print("Price:", cheapest["Product_Price"])

# 11. Highest rated product
highest_rated = df.loc[df["Product_Rating"].idxmax()]

print("\nHighest Rated Product:")
print("Name:", highest_rated["Product_Name"])
print("Rating:", highest_rated["Product_Rating"])

# 12. Most common category
most_common_category = df["Category"].value_counts().idxmax()

print("\nMost Common Category:")
print(most_common_category)

# 13. Most common brand
most_common_brand = df["Brand"].value_counts().idxmax()

print("\nMost Common Brand:")
print(most_common_brand)

# 14. Stock percentage
stock_percentage = (
    df["Availability"].value_counts(normalize=True) * 100
)

# 15. Products by Category - Bar Chart

category_counts = df["Category"].value_counts()

plt.figure(figsize=(10, 6))

category_counts.plot(kind="bar")

plt.title("Number of Products by Category")
plt.xlabel("Category")
plt.ylabel("Number of Products")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/category_distribution.png")

plt.show()

# 16. Product Price Distribution - Histogram

plt.figure(figsize=(10, 6))

plt.hist(df["Product_Price"], bins=10)

plt.title("Product Price Distribution")
plt.xlabel("Product Price")
plt.ylabel("Number of Products")

plt.tight_layout()
plt.savefig("charts/price_distribution.png")

plt.show()

# 17. Product Availability - Pie Chart

availability_counts = df["Availability"].value_counts()

plt.figure(figsize=(7, 7))

plt.pie(
    availability_counts,
    labels=availability_counts.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Product Availability")

plt.tight_layout()
plt.savefig("charts/availability.png")

plt.show()

# 18. Product Rating Distribution - Bar Chart

rating_counts = df["Product_Rating"].value_counts().sort_index()

plt.figure(figsize=(10, 6))

rating_counts.plot(kind="bar")

plt.title("Product Rating Distribution")
plt.xlabel("Product Rating")
plt.ylabel("Number of Products")

plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/rating_distribution.png")
plt.show()

# Rating vs Price Scatter Plot

plt.figure(figsize=(10, 6))

plt.scatter(
    df["Product_Price"],
    df["Product_Rating"]
)

plt.title("Price vs Product Rating")
plt.xlabel("Product Price")
plt.ylabel("Product Rating")

plt.tight_layout()

plt.savefig("charts/rating_vs_price.png")

plt.show()

print("\nAvailability Percentage:")
print(stock_percentage)

print("\n" + "=" * 50)
print("ANALYSIS COMPLETED")
print("=" * 50)