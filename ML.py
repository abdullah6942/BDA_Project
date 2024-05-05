from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import MultilayerPerceptronRegressor
from pyspark.ml.evaluation import RegressionEvaluator
from pymongo import MongoClient

# Connect to MongoDB and retrieve data
client = MongoClient('localhost', 27017)
db = client['audio']
collection = db['audio_collection']
cursor = collection.find()

# Create a Spark session
spark = SparkSession.builder \
    .appName("MusicRecommendation") \
    .getOrCreate()

# Convert MongoDB data to a Spark DataFrame
data = []
for document in cursor:
    features = document['features'][0]  #  'features' is an array of numbers
    data.append((features,))  # Add each feature array as a tuple to the data list

# Define the schema for the DataFrame
schema = ["features"]
df = spark.createDataFrame(data, schema)

# Split the data into training and testing sets
train_data, test_data = df.randomSplit([0.8, 0.2])

# Define the features vector
assembler = VectorAssembler(inputCols=["features"], outputCol="features_vector")
train_data = assembler.transform(train_data)
test_data = assembler.transform(test_data)

# Define the ANN model
layers = [len(train_data.select('features_vector').first()[0]), 64, 32, 1]  # Define the layers of the ANN
ann = MultilayerPerceptronRegressor(layers=layers, seed=123)

# Train the ANN model
ann_model = ann.fit(train_data)

# Make predictions on the test data
predictions = ann_model.transform(test_data)

# Evaluate the model using a regression evaluator
evaluator = RegressionEvaluator(labelCol="features_vector", predictionCol="prediction", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Stop the Spark session
spark.stop()
