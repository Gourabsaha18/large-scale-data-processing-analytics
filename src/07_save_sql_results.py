# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession

# pyrefly: ignore [missing-import]
from pyspark.sql.functions import round, avg, sum, count


# ============================================================
# CREATE SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("SaveSQLAnalyticsResults")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# ============================================================
# LOAD ANALYTICS DATA
# ============================================================

input_path = "data/processed/order_analytics"

df = spark.read.parquet(input_path)


print("\n========== DATA LOADED ==========")
print("Total rows:", df.count())


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

output_path = "data/processed/sql_results"


# ============================================================
# 1. REVENUE BY PRODUCT CATEGORY
# ============================================================

revenue_by_category = (
    df.groupBy("product_category_name")
    .agg(
        round(sum("price"), 2).alias("total_revenue"),
        count("*").alias("order_items")
    )
    .orderBy("total_revenue", ascending=False)
)

print("\n========== REVENUE BY CATEGORY ==========")

revenue_by_category.show(20, truncate=False)

revenue_by_category.write.mode("overwrite").parquet(
    f"{output_path}/revenue_by_category"
)


# ============================================================
# 2. REVENUE BY CUSTOMER STATE
# ============================================================

revenue_by_state = (
    df.groupBy("customer_state")
    .agg(
        count("*").alias("order_items"),
        round(sum("price"), 2).alias("total_revenue")
    )
    .orderBy("total_revenue", ascending=False)
)

print("\n========== REVENUE BY STATE ==========")

revenue_by_state.show(20)

revenue_by_state.write.mode("overwrite").parquet(
    f"{output_path}/revenue_by_state"
)


# ============================================================
# 3. PAYMENT METHOD ANALYSIS
# ============================================================

payment_analysis = (
    df.groupBy("payment_type")
    .agg(
        count("*").alias("order_items"),
        round(avg("price"), 2).alias("average_price")
    )
    .orderBy("order_items", ascending=False)
)

print("\n========== PAYMENT METHOD ANALYSIS ==========")

payment_analysis.show()

payment_analysis.write.mode("overwrite").parquet(
    f"{output_path}/payment_analysis"
)


# ============================================================
# 4. DELIVERY PERFORMANCE
# ============================================================

delivery_performance = (
    df.groupBy("delivery_performance")
    .agg(
        count("*").alias("order_items"),
        round(avg("delivery_days"), 2).alias("average_delivery_days")
    )
    .orderBy("order_items", ascending=False)
)

print("\n========== DELIVERY PERFORMANCE ==========")

delivery_performance.show()

delivery_performance.write.mode("overwrite").parquet(
    f"{output_path}/delivery_performance"
)


# ============================================================
# 5. TOP 10 PRODUCT CATEGORIES
# ============================================================

top_categories = (
    df.groupBy("product_category_name")
    .agg(
        round(sum("price"), 2).alias("revenue")
    )
    .orderBy("revenue", ascending=False)
    .limit(10)
)

print("\n========== TOP 10 PRODUCT CATEGORIES ==========")

top_categories.show(truncate=False)

top_categories.write.mode("overwrite").parquet(
    f"{output_path}/top_categories"
)


# ============================================================
# COMPLETED
# ============================================================

print("\n========== SAVING COMPLETED ==========")

print(f"SQL analytics results saved to: {output_path}")


# ============================================================
# STOP SPARK
# ============================================================

spark.stop()