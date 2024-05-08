from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType
from pyspark.ml.linalg import Vectors, VectorUDT

# Create a Spark session
spark = SparkSession.builder \
    .appName("MusicRecommendationModel") \
    .getOrCreate()

# Load data from MongoDB into a Spark DataFrame
df = spark.read.format("mongo").option("uri", "mongodb://localhost:27017/music_features.audio_features").load()

# Extract 'oid' field from '_id' column and cast it to integer
df = df.withColumn("_id", col("_id.oid").cast("int"))

# Convert 'audio_file' column to DoubleType
df = df.withColumn("filename", col("filename").cast(DoubleType()))

# Define a function to convert arrays and strings to numerical values or Vectors
def array_to_vector(arr):
    if isinstance(arr, list):
        return Vectors.dense(arr)
    elif isinstance(arr, float) or isinstance(arr, int):
        return float(arr)
    elif isinstance(arr, str):
        try:
            return float(arr)
        except ValueError:
            return None  # Handle cases where conversion to float is not possible
    else:
        return None

# Create a user-defined function (UDF) to convert the 'features' column to appropriate types
array_to_vector_udf = udf(array_to_vector, DoubleType())
df = df.withColumn("features", array_to_vector_udf(col("features")))

# Sample data using aggregated stage for training/testing
sampled_df = df.sampleBy("_id", fractions={"user_id_1": 0.8, "user_id_2": 0.8}, seed=42)  # 80% for training

# Split data into training and testing sets
train_data, test_data = sampled_df.randomSplit([0.8, 0.2])

# Apply ALS (Alternating Least Squares) for collaborative filtering
als = ALS(maxIter=10, regParam=0.01, userCol="_id", itemCol="features", ratingCol="filename", coldStartStrategy="drop")
model = als.fit(train_data)

# Generate recommendations
userRecs = model.recommendForAllUsers(10)  # Top 10 recommendations for each user
itemRecs = model.recommendForAllItems(10)  # Top 10 recommendations for each item

# Evaluate the model
predictions = model.transform(test_data)
evaluator = RegressionEvaluator(metricName="mse", labelCol="filename", predictionCol="prediction")
mse = evaluator.evaluate(predictions)
print(f"Mean Squared Error (MSE): {mse}")

# Make predictions for a specific user
user_id = 123  # Example user ID
user_predictions = model.recommendForUserSubset(spark.createDataFrame([[user_id]], ["_id"])).collect()[0]["recommendations"]
print("User Recommendations:")
for row in user_predictions:
    print(row)

# Find closest files based on item embeddings
item_id = 456  # Example item ID
closest_files = model.findSimilarItems(item_id, 5).select("features").rdd.flatMap(lambda x: x).collect()
print("Closest Files:", closest_files)

# Stop the Spark session
spark.stop()

