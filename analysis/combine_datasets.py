import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
SOURCE_FILES = {
    "scrapingcourse_products.csv": "ScrapingCourse",
    "barn2_products.csv": "Barn2",
    "books_products.csv": "Books to Scrape",
    "scrapingsandbox_products.csv": "Scraping Sandbox",
}


def combine_datasets():
    datasets = []
    source_counts = {}

    for filename, website_name in SOURCE_FILES.items():
        file_path = DATA_DIR / filename
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Required source file not found: {file_path}"
            )

        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"Required source file is empty: {file_path}")

        df["Website_Name"] = website_name
        datasets.append(df)
        source_counts[website_name] = len(df)

    all_products = pd.concat(
        datasets,
        ignore_index=True,
        sort=False,
    )
    combined_counts = all_products["Website_Name"].value_counts().to_dict()

    if combined_counts != source_counts:
        raise RuntimeError(
            "Combined website counts do not match source counts: "
            f"{combined_counts}"
        )

    output_file = DATA_DIR / "all_products.csv"
    all_products.to_csv(output_file, index=False)

    print("Combined products:", len(all_products))
    print("Products by website:")
    print(all_products["Website_Name"].value_counts())
    print("Saved to:", output_file)

    return all_products


if __name__ == "__main__":
    combine_datasets()
