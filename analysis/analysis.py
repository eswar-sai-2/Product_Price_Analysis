import pandas as pd

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

print("\nAvailability Percentage:")
print(stock_percentage)

print("\n" + "=" * 50)
print("ANALYSIS COMPLETED")
print("=" * 50)