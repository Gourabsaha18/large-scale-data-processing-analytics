from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month

RAW_PATH = "data/raw/sales.csv"
OUTPUT_PATH = "data/processed/sales_parquet"

spark = (
    SparkSession.builder
    .appName("LargeScaleSalesETL")
    .getOrCreate()
)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(RAW_PATH)
)

print("Raw record count:", df.count())
df.printSchema()

# Basic cleaning
df = df.dropDuplicates()
df = df.dropna(how="all")

# Standardize numeric columns when present
for column_name in ["Quantity", "Unit_Price", "Discount", "Sales", "Profit"]:
    if column_name in df.columns:
        df = df.withColumn(column_name, col(column_name).cast("double"))

# Derive revenue if the required fields exist
if "Quantity" in df.columns and "Unit_Price" in df.columns:
    df = df.withColumn("Revenue", col("Quantity") * col("Unit_Price"))
elif "Sales" in df.columns:
    df = df.withColumn("Revenue", col("Sales"))

# Derive date attributes if Order_Date exists
if "Order_Date" in df.columns:
    df = df.withColumn("Year", year("Order_Date"))
    df = df.withColumn("Month", month("Order_Date"))

df.write.mode("overwrite").parquet(OUTPUT_PATH)

print("Processed record count:", df.count())
print(f"Processed data written to: {OUTPUT_PATH}")

spark.stop()
