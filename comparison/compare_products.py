import pandas as pd
from pathlib import Path

               
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "comparison"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

                      
df = pd.read_csv(DATA_DIR / "cleaned_products.csv")

                          
df["Product_Price"] = pd.to_numeric(
    df["Product_Price"], errors="coerce"
)

                         
comparison = df[
    df["Website_Name"].isin(["Barn2", "ScrapingCourse"])
].copy()

                                              
comparison = comparison.dropna(
    subset=["Product_Name", "Product_Price"]
)

                                   
grouped = comparison.groupby(
    ["Product_Name", "Website_Name"]
)["Product_Price"].mean().unstack()

                                          
if "Barn2" in grouped.columns and "ScrapingCourse" in grouped.columns:

    matched = grouped.dropna(
        subset=["Barn2", "ScrapingCourse"]
    ).copy()

    matched["Price_Difference"] = (
        matched["ScrapingCourse"] - matched["Barn2"]
    )

    matched["Cheaper_Website"] = matched.apply(
        lambda row: (
            "Barn2"
            if row["Barn2"] < row["ScrapingCourse"]
            else (
                "ScrapingCourse"
                if row["ScrapingCourse"] < row["Barn2"]
                else "Same price"
            )
        ),
        axis=1
    )

    matched = matched.reset_index()

    matched.to_csv(
        OUTPUT_DIR / "matched_product_comparison.csv",
        index=False
    )

    print("=" * 55)
    print("MATCHED PRODUCT PRICE COMPARISON")
    print("=" * 55)

    print("Matching products:", len(matched))

    print("\nFirst 15 matching products:")
    print(matched.head(15).to_string(index=False))

    print("\nCheaper website counts:")
    print(matched["Cheaper_Website"].value_counts())

    print("\nSaved to:")
    print(OUTPUT_DIR / "matched_product_comparison.csv")

else:
    print("The required website columns were not found.")