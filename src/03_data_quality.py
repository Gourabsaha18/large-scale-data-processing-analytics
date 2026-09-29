# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession
# pyrefly: ignore [missing-import]
from pyspark.sql.functions import col


# --------------------------------------------------
# 1. Create Spark Session
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("OlistDataQuality")
    .getOrCreate()
)


# --------------------------------------------------
# 2. Load Orders Dataset
# --------------------------------------------------

orders_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("data/raw/olist_orders_dataset.csv")
)


# --------------------------------------------------
# 3. Delivered Orders with Missing Carrier Date
# --------------------------------------------------

print("\n========== DELIVERED ORDERS WITH MISSING CARRIER DATE ==========\n")

delivered_missing_carrier = (
    orders_df
    .filter(
        (col("order_status") == "delivered") &
        col("order_delivered_carrier_date").isNull()
    )
)

delivered_missing_carrier.show(truncate=False)


# --------------------------------------------------
# 4. Delivered Orders with Missing Customer Delivery Date
# --------------------------------------------------

print("\n========== DELIVERED ORDERS WITH MISSING CUSTOMER DELIVERY DATE ==========\n")

delivered_missing_customer = (
    orders_df
    .filter(
        (col("order_status") == "delivered") &
        col("order_delivered_customer_date").isNull()
    )
)

delivered_missing_customer.show(truncate=False)


# --------------------------------------------------
# 5. Count Results
# --------------------------------------------------

print("\n========== COUNTS ==========\n")

print(
    "Delivered orders missing carrier date:",
    delivered_missing_carrier.count()
)

print(
    "Delivered orders missing customer delivery date:",
    delivered_missing_customer.count()
)


# --------------------------------------------------
# 6. Stop Spark
# --------------------------------------------------

spark.stop()