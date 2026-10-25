import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

               
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "visualizations"

                                       
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

                   
df = pd.read_csv(DATA_DIR / "cleaned_products.csv")

                            
df["Product_Price"] = pd.to_numeric(
    df["Product_Price"], errors="coerce"
)

df["Product_Rating"] = pd.to_numeric(
    df["Product_Rating"], errors="coerce"
)

                              
website_stats = df.groupby("Website_Name").agg(
    Product_Count=("Product_Name", "count"),
    Average_Price=("Product_Price", "mean"),
    Average_Rating=("Product_Rating", "mean")
)

                                                    
                                   
                                                    

plt.figure(figsize=(10, 6))

website_stats["Product_Count"].plot(
    kind="bar",
    edgecolor="black"
)

plt.title("Number of Products Collected by Website")
plt.xlabel("Website")
plt.ylabel("Number of Products")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "product_count_by_website.png",
    dpi=300
)

plt.show()
plt.close()

                                                    
                                   
                                                    

plt.figure(figsize=(10, 6))

website_stats["Average_Price"].plot(
    kind="bar",
    edgecolor="black"
)

plt.title("Average Recorded Product Price by Website")
plt.xlabel("Website")
plt.ylabel("Average Price (recorded units)")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "average_price_by_website.png",
    dpi=300
)

plt.show()
plt.close()

                                                    
                                    
                                                    

plt.figure(figsize=(10, 6))

website_stats["Average_Rating"].dropna().plot(
    kind="bar",
    edgecolor="black"
)

plt.title("Average Product Rating by Website")
plt.xlabel("Website")
plt.ylabel("Average Rating (out of 5)")
plt.ylim(0, 5)
plt.xticks(rotation=20, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "average_rating_by_website.png",
    dpi=300
)

plt.show()
plt.close()

                                                    
                                     
                                                    

plt.figure(figsize=(10, 6))

df["Product_Price"].dropna().plot(
    kind="hist",
    bins=20,
    edgecolor="black"
)

plt.title("Distribution of Recorded Product Prices")
plt.xlabel("Price (recorded units)")
plt.ylabel("Number of Products")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "price_distribution.png",
    dpi=300
)

plt.show()
plt.close()

                                                    
                                         
                                                    

top_10 = df.nlargest(
    10, "Product_Price"
).sort_values("Product_Price")

plt.figure(figsize=(12, 7))

plt.barh(
    top_10["Product_Name"],
    top_10["Product_Price"],
    edgecolor="black"
)

plt.title("Top 10 Most Expensive Products")
plt.xlabel("Price (recorded units)")
plt.ylabel("Product Name")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "top_10_expensive_products.png",
    dpi=300
)

plt.show()
plt.close()

print("\n" + "=" * 50)
print("DATA VISUALIZATION COMPLETED!")
print("=" * 50)

print("Graphs saved in:", OUTPUT_DIR)

for file in OUTPUT_DIR.glob("*.png"):
    print("-", file.name)