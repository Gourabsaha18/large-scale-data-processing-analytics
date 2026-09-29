# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession


# --------------------------------------------------
# 1. Create Spark Session
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("OlistDataLoading")
    .getOrCreate()
)


# --------------------------------------------------
# 2. Function to load CSV files
# --------------------------------------------------

def load_csv(file_name):
    """
    Load a CSV file from the data/raw directory
    and return it as a Spark DataFrame.
    """

    file_path = f"data/raw/{file_name}"

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(file_path)
    )

    return df


# --------------------------------------------------
# 3. Load all datasets
# --------------------------------------------------

customers_df = load_csv("olist_customers_dataset.csv")

geolocation_df = load_csv("olist_geolocation_dataset.csv")

order_items_df = load_csv("olist_order_items_dataset.csv")

payments_df = load_csv("olist_order_payments_dataset.csv")

reviews_df = load_csv("olist_order_reviews_dataset.csv")

orders_df = load_csv("olist_orders_dataset.csv")

products_df = load_csv("olist_products_dataset.csv")

sellers_df = load_csv("olist_sellers_dataset.csv")

category_translation_df = load_csv(
    "product_category_name_translation.csv"
)


# --------------------------------------------------
# 4. Display row counts
# --------------------------------------------------

print("\n========== DATASET ROW COUNTS ==========\n")

print("Customers:", customers_df.count())

print("Geolocation:", geolocation_df.count())

print("Order Items:", order_items_df.count())

print("Payments:", payments_df.count())

print("Reviews:", reviews_df.count())

print("Orders:", orders_df.count())

print("Products:", products_df.count())

print("Sellers:", sellers_df.count())

print("Category Translation:", category_translation_df.count())


# --------------------------------------------------
# 5. Stop Spark
# --------------------------------------------------

spark.stop()