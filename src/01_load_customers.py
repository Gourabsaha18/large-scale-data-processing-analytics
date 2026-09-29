# pyrefly: ignore [missing-import]
from pyspark.sql import SparkSession

# 1. Create Spark session
spark = (
    SparkSession.builder
    .appName("OlistCustomerAnalysis")
    .getOrCreate()
)

# 2. Path to the customer dataset
file_path = "data/raw/olist_customers_dataset.csv"

# 3. Read the CSV file
customers_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(file_path)
)

# 4. Display first 5 rows
print("\n--- First 5 Rows ---")
customers_df.show(5, truncate=False)

# 5. Display the schema
print("\n--- Dataset Schema ---")
customers_df.printSchema()

# 6. Count records
print("\n--- Number of Customers ---")
print(customers_df.count())

# 7. Stop Spark
spark.stop()