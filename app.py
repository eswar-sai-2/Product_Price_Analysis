import math
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from flask import Flask, abort, g, render_template, request, send_from_directory

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "cleaned_products.csv"
VISUALIZATION_DIR = BASE_DIR / "visualizations"
PER_PAGE = 20
COMPARISON_PER_PAGE = 12
CHART_FILES = {
    "average_price_by_website.png",
    "average_rating_by_website.png",
    "price_distribution.png",
    "product_count_by_website.png",
    "top_10_expensive_products.png",
}


class DatasetError(Exception):
    """Raised when the application cannot load its canonical dataset."""


def load_products():
    """Load and normalize the canonical dataset once per request."""
    if "products_df" not in g:
        if not DATA_FILE.is_file():
            raise DatasetError("The product dataset is currently unavailable.")

        try:
            df = pd.read_csv(DATA_FILE)
        except (
            OSError,
            UnicodeDecodeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ) as error:
            raise DatasetError(
                "The product dataset could not be read."
            ) from error

        required_columns = [
            "Product_Name",
            "Product_Price",
            "Product_Rating",
            "Product_URL",
            "Website_Name",
            "Date_Scraped",
            "Availability",
        ]
        for column in required_columns:
            if column not in df.columns:
                df[column] = pd.NA

        df["Product_Price"] = pd.to_numeric(
            df["Product_Price"], errors="coerce"
        )
        df["Product_Rating"] = pd.to_numeric(
            df["Product_Rating"], errors="coerce"
        )
        g.products_df = df

    return g.products_df


def safe_product_url(value):
    """Return only absolute HTTP(S) links for product data."""
    if pd.isna(value):
        return None

    url = str(value).strip()
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
    except ValueError:
        return None

    if parts.scheme.lower() not in {"http", "https"} or not hostname:
        return None
    return url


def _website_names(df):
    return sorted(
        df["Website_Name"].dropna().astype(str).str.strip().unique().tolist(),
        key=str.casefold,
    )


def _products_for_template(df):
    products = df.to_dict(orient="records")
    for product in products:
        for key, value in product.items():
            if pd.isna(value):
                product[key] = None
        product["safe_product_url"] = safe_product_url(
            product.get("Product_URL")
        )
    return products


def _parse_filter(value, label, errors, minimum=None, maximum=None):
    if not value:
        return None

    try:
        parsed = float(value)
    except ValueError:
        errors.append(f"{label} must be a number.")
        return None

    if not math.isfinite(parsed):
        errors.append(f"{label} must be a finite number.")
        return None
    if minimum is not None and parsed < minimum:
        errors.append(f"{label} must be at least {minimum}.")
        return None
    if maximum is not None and parsed > maximum:
        errors.append(f"{label} must be no more than {maximum}.")
        return None
    return parsed


@app.errorhandler(DatasetError)
def handle_dataset_error(error):
    app.logger.error("Dataset request failed: %s", error)
    return (
        render_template(
            "error.html",
            title="Product data unavailable",
            message=str(error),
        ),
        503,
    )


@app.route("/")
def home():
    """Display the dynamically calculated overview dashboard."""
    df = load_products()
    prices = df["Product_Price"].dropna()
    ratings = df["Product_Rating"].dropna()
    ratings = ratings[ratings.between(0, 5)]

    stats = {
        "total_products": len(df),
        "total_websites": df["Website_Name"].nunique(),
        "average_price": prices.mean() if not prices.empty else None,
        "average_rating": ratings.mean() if not ratings.empty else None,
        "highest_price": prices.max() if not prices.empty else None,
        "lowest_price": prices.min() if not prices.empty else None,
        "rated_products": len(ratings),
    }

    website_counts = (
        df["Website_Name"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
        .sort_values(ascending=False)
    )
    chart_data = {
        "labels": website_counts.index.tolist(),
        "values": website_counts.astype(int).tolist(),
    }
    products = _products_for_template(
        df.dropna(subset=["Product_Name"]).head(8)
    )

    return render_template(
        "index.html",
        stats=stats,
        website_counts=website_counts.to_dict(),
        chart_data=chart_data,
        products=products,
    )


@app.route("/products")
def product_list():
    """Search, filter, sort, and paginate the canonical product data."""
    df = load_products()
    errors = []

    search = request.args.get("search", "").strip()
    selected_website = request.args.get("website", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    min_rating = request.args.get("min_rating", "").strip()
    selected_availability = request.args.get("availability", "").strip()
    sort_by = request.args.get("sort_by", "name").strip()
    page = max(1, request.args.get("page", 1, type=int) or 1)

    websites = _website_names(df)
    availabilities = sorted(
        df["Availability"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .unique()
        .tolist(),
        key=str.casefold,
    )

    min_price_value = _parse_filter(
        min_price, "Minimum price", errors, minimum=0
    )
    max_price_value = _parse_filter(
        max_price, "Maximum price", errors, minimum=0
    )
    min_rating_value = _parse_filter(
        min_rating, "Minimum rating", errors, minimum=0, maximum=5
    )
    if (
        min_price_value is not None
        and max_price_value is not None
        and min_price_value > max_price_value
    ):
        errors.append("Minimum price cannot exceed maximum price.")
        min_price_value = None
        max_price_value = None

    if search:
        df = df[
            df["Product_Name"]
            .astype("string")
            .str.contains(search, case=False, na=False, regex=False)
        ]

    if selected_website:
        if selected_website in websites:
            df = df[df["Website_Name"].astype(str) == selected_website]
        else:
            errors.append("The selected website is not in the dataset.")
            df = df.iloc[0:0]

    if min_price_value is not None:
        df = df[df["Product_Price"] >= min_price_value]
    if max_price_value is not None:
        df = df[df["Product_Price"] <= max_price_value]
    if min_rating_value is not None:
        df = df[df["Product_Rating"] >= min_rating_value]
    if selected_availability:
        if selected_availability in availabilities:
            availability_values = (
                df["Availability"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .replace("", "Unknown")
            )
            df = df[availability_values == selected_availability]
        else:
            errors.append("The selected availability is not in the dataset.")
            df = df.iloc[0:0]

    sort_columns = {
        "price_low": ("Product_Price", True),
        "price_high": ("Product_Price", False),
        "rating": ("Product_Rating", False),
    }
    if sort_by in sort_columns:
        column, ascending = sort_columns[sort_by]
    else:
        if sort_by != "name":
            errors.append("Unknown sort option; showing products by name.")
        sort_by = "name"
        column, ascending = "Product_Name", True
    df = df.sort_values(column, ascending=ascending, na_position="last")

    total_results = len(df)
    total_pages = max(1, math.ceil(total_results / PER_PAGE))
    page = min(page, total_pages)
    start = (page - 1) * PER_PAGE
    products = _products_for_template(df.iloc[start : start + PER_PAGE])

    return render_template(
        "product.html",
        products=products,
        websites=websites,
        availabilities=availabilities,
        search=search,
        selected_website=selected_website,
        selected_availability=selected_availability,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
        errors=errors,
    )


@app.route("/analytics")
def analytics():
    load_products()
    charts = [
        {
            "title": "Average recorded price by website",
            "description": (
                "Static output from the visualization script. Currency "
                "metadata is unavailable; do not compare these amounts "
                "across websites as normalized prices."
            ),
            "file": "average_price_by_website.png",
            "alt": "Bar chart showing average recorded product price by website.",
        },
        {
            "title": "Average available rating by website",
            "description": (
                "Ratings are calculated only where recorded; ScrapingCourse "
                "has no ratings in the current dataset."
            ),
            "file": "average_rating_by_website.png",
            "alt": "Bar chart showing average product rating by website.",
        },
        {
            "title": "Recorded price distribution",
            "description": (
                "Distribution of recorded prices across the dataset; "
                "currency units are not identified."
            ),
            "file": "price_distribution.png",
            "alt": "Histogram of recorded product prices.",
        },
        {
            "title": "Products collected by website",
            "description": "Product row counts grouped by source website.",
            "file": "product_count_by_website.png",
            "alt": "Bar chart of collected product counts by website.",
        },
        {
            "title": "Top 10 recorded prices",
            "description": (
                "Products with the highest recorded price values. "
                "Amounts are not currency-normalized."
            ),
            "file": "top_10_expensive_products.png",
            "alt": "Bar chart listing the ten products with highest recorded prices.",
        },
    ]
    return render_template("analytics.html", charts=charts)


@app.route("/visualizations/<path:filename>")
def visualization_file(filename):
    if filename not in CHART_FILES:
        abort(404)
    return send_from_directory(VISUALIZATION_DIR, filename)


@app.route("/comparison")
def comparison():
    df = load_products()
    search = request.args.get("search", "").strip()
    page = max(1, request.args.get("page", 1, type=int) or 1)

    candidates = df.dropna(subset=["Product_Name", "Website_Name"]).copy()
    candidates["_match_key"] = (
        candidates["Product_Name"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )
    if search:
        candidates = candidates[
            candidates["Product_Name"]
            .astype("string")
            .str.contains(search, case=False, na=False, regex=False)
        ]

    groups = []
    for _, group in candidates.groupby("_match_key", sort=True):
        if group["Website_Name"].nunique() < 2:
            continue
        first_name = str(group.iloc[0]["Product_Name"]).strip()
        rows = _products_for_template(
            group.sort_values(
                "Website_Name", key=lambda col: col.astype(str).str.casefold()
            ).drop(columns=["_match_key"])
        )
        groups.append({"name": first_name, "products": rows})

    total_results = len(groups)
    total_pages = max(1, math.ceil(total_results / COMPARISON_PER_PAGE))
    page = min(page, total_pages)
    start = (page - 1) * COMPARISON_PER_PAGE

    return render_template(
        "comparison.html",
        groups=groups[start : start + COMPARISON_PER_PAGE],
        search=search,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
    )


@app.route("/data-sources")
def data_sources():
    df = load_products()
    counts = (
        df["Website_Name"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
        .to_dict()
    )
    sources = []
    for website in _website_names(df):
        site_rows = df[df["Website_Name"].astype(str).str.strip() == website]
        dates = []
        if "Date_Scraped" in site_rows:
            parsed_dates = pd.to_datetime(
                site_rows["Date_Scraped"], errors="coerce"
            ).dropna()
            dates = sorted(parsed_dates.dt.strftime("%Y-%m-%d").unique())
        sources.append(
            {
                "name": website,
                "count": int(counts.get(website, 0)),
                "dates": dates,
            }
        )

    fields = df.columns.tolist()
    return render_template(
        "data_sources.html",
        sources=sources,
        fields=fields,
        total_products=len(df),
    )


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=False)
