# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession
# pyrefly: ignore [missing-import]
from pyspark.sql.functions import (
    col,
    sum,
    count,
    avg,
    round
)


# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("OlistOrderAnalytics")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# --------------------------------------------------
# 2. DEFINE PATHS
# --------------------------------------------------

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed/orders_cleaned"
OUTPUT_PATH = "data/processed/order_analytics"


# --------------------------------------------------
# 3. LOAD PROCESSED ORDERS
# --------------------------------------------------

orders = spark.read.parquet(PROCESSED_PATH)


# --------------------------------------------------
# 4. LOAD RAW DATASETS
# --------------------------------------------------

customers = spark.read.csv(
    f"{RAW_PATH}/olist_customers_dataset.csv",
    header=True,
    inferSchema=True
)

order_items = spark.read.csv(
    f"{RAW_PATH}/olist_order_items_dataset.csv",
    header=True,
    inferSchema=True
)

products = spark.read.csv(
    f"{RAW_PATH}/olist_products_dataset.csv",
    header=True,
    inferSchema=True
)

payments = spark.read.csv(
    f"{RAW_PATH}/olist_order_payments_dataset.csv",
    header=True,
    inferSchema=True
)


# --------------------------------------------------
# 5. SELECT REQUIRED CUSTOMER COLUMNS
# --------------------------------------------------

customers_selected = customers.select(
    "customer_id",
    "customer_unique_id",
    "customer_city",
    "customer_state"
)


# --------------------------------------------------
# 6. SELECT REQUIRED PRODUCT COLUMNS
# --------------------------------------------------

products_selected = products.select(
    "product_id",
    "product_category_name"
)


# --------------------------------------------------
# 7. SELECT REQUIRED ORDER ITEM COLUMNS
# --------------------------------------------------

order_items_selected = order_items.select(
    "order_id",
    "order_item_id",
    "product_id",
    "price",
    "freight_value"
)


# --------------------------------------------------
# 8. SELECT REQUIRED PAYMENT COLUMNS
# --------------------------------------------------

payments_selected = payments.select(
    "order_id",
    "payment_type",
    "payment_installments",
    "payment_value"
)


# --------------------------------------------------
# 9. JOIN ORDERS WITH CUSTOMERS
# --------------------------------------------------

analytics = orders.join(
    customers_selected,
    on="customer_id",
    how="left"
)


# --------------------------------------------------
# 10. JOIN WITH ORDER ITEMS
# --------------------------------------------------

analytics = analytics.join(
    order_items_selected,
    on="order_id",
    how="left"
)


# --------------------------------------------------
# 11. JOIN WITH PRODUCTS
# --------------------------------------------------

analytics = analytics.join(
    products_selected,
    on="product_id",
    how="left"
)


# --------------------------------------------------
# 12. JOIN WITH PAYMENTS
# --------------------------------------------------

analytics = analytics.join(
    payments_selected,
    on="order_id",
    how="left"
)


# --------------------------------------------------
# 13. DISPLAY ANALYTICS DATA
# --------------------------------------------------

print("\n========== ANALYTICS DATA ==========\n")

analytics.select(
    "order_id",
    "customer_state",
    "product_category_name",
    "price",
    "freight_value",
    "payment_type",
    "delivery_days",
    "delivery_performance"
).show(10, truncate=False)


# --------------------------------------------------
# 14. TOTAL REVENUE
# --------------------------------------------------

print("\n========== TOTAL REVENUE ==========\n")

total_revenue = (
    analytics
    .select(round(sum("price"), 2).alias("total_revenue"))
)

total_revenue.show()


# --------------------------------------------------
# 15. REVENUE BY PRODUCT CATEGORY
# --------------------------------------------------

print("\n========== REVENUE BY PRODUCT CATEGORY ==========\n")

category_revenue = (
    analytics
    .groupBy("product_category_name")
    .agg(
        round(sum("price"), 2).alias("total_revenue"),
        count("order_id").alias("order_count")
    )
    .orderBy(col("total_revenue").desc())
)

category_revenue.show(20, truncate=False)


# --------------------------------------------------
# 16. ORDERS BY CUSTOMER STATE
# --------------------------------------------------

print("\n========== ORDERS BY CUSTOMER STATE ==========\n")

state_orders = (
    analytics
    .groupBy("customer_state")
    .agg(
        count("order_id").alias("order_count"),
        round(sum("price"), 2).alias("total_revenue")
    )
    .orderBy(col("order_count").desc())
)

state_orders.show(20)


# --------------------------------------------------
# 17. PAYMENT METHOD ANALYSIS
# --------------------------------------------------

print("\n========== PAYMENT METHOD ANALYSIS ==========\n")

payment_analysis = (
    analytics
    .groupBy("payment_type")
    .agg(
        count("order_id").alias("order_count"),
        round(avg("payment_value"), 2).alias("average_payment")
    )
    .orderBy(col("order_count").desc())
)

payment_analysis.show()


# --------------------------------------------------
# 18. DELIVERY PERFORMANCE
# --------------------------------------------------

print("\n========== DELIVERY PERFORMANCE ==========\n")

delivery_analysis = (
    analytics
    .groupBy("delivery_performance")
    .agg(
        count("order_id").alias("order_count"),
        round(avg("delivery_days"), 2).alias("average_delivery_days")
    )
    .orderBy(col("order_count").desc())
)

delivery_analysis.show()


# --------------------------------------------------
# 19. SAVE ANALYTICS DATA
# --------------------------------------------------

print("\n========== SAVING ANALYTICS DATA ==========\n")

(
    analytics
    .write
    .mode("overwrite")
    .parquet(OUTPUT_PATH)
)

print(f"Analytics dataset saved to: {OUTPUT_PATH}")


# --------------------------------------------------
# 20. STOP SPARK
# --------------------------------------------------

spark.stop()