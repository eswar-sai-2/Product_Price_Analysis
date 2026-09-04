import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/cleaned_products.csv")

print("=" * 60)
print("PRODUCT COMPARISON SYSTEM")
print("=" * 60)

# Show available products
print("\nAvailable Products:")
for i, product in enumerate(df["Product_Name"].head(20), start=1):
    print(f"{i}. {product}")

# Get product names from user
product1 = input("\nEnter first product name: ")
product2 = input("Enter second product name: ")

# Find products
p1 = df[df["Product_Name"].str.lower() == product1.lower()]
p2 = df[df["Product_Name"].str.lower() == product2.lower()]

# Check whether products exist
if p1.empty or p2.empty:
    print("\nProduct not found.")
    print("Please enter the product name exactly as shown above.")

else:
    p1 = p1.iloc[0]
    p2 = p2.iloc[0]

    print("\n" + "=" * 60)
    print("PRODUCT COMPARISON")
    print("=" * 60)

    print("\nProduct 1")
    print("-" * 30)
    print("Name:", p1["Product_Name"])
    print("Price:", p1["Product_Price"])
    print("Rating:", p1["Product_Rating"])
    print("Brand:", p1["Brand"])
    print("Category:", p1["Category"])
    print("Availability:", p1["Availability"])

    print("\nProduct 2")
    print("-" * 30)
    print("Name:", p2["Product_Name"])
    print("Price:", p2["Product_Price"])
    print("Rating:", p2["Product_Rating"])
    print("Brand:", p2["Brand"])
    print("Category:", p2["Category"])
    print("Availability:", p2["Availability"])

    # Price comparison
    price_difference = abs(
        p1["Product_Price"] - p2["Product_Price"]
    )

    print("\n" + "=" * 60)
    print("COMPARISON RESULT")
    print("=" * 60)

    print(f"\nPrice Difference: {price_difference:.2f}")

    if p1["Product_Price"] < p2["Product_Price"]:
        print("Lower Price:", p1["Product_Name"])
    elif p2["Product_Price"] < p1["Product_Price"]:
        print("Lower Price:", p2["Product_Name"])
    else:
        print("Both products have the same price.")

    if p1["Product_Rating"] > p2["Product_Rating"]:
        print("Higher Rated:", p1["Product_Name"])
    elif p2["Product_Rating"] > p1["Product_Rating"]:
        print("Higher Rated:", p2["Product_Name"])
    else:
        print("Both products have the same rating.")

    print("\n" + "=" * 60)