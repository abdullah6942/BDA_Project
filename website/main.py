from flask import Flask, session, render_template, redirect, url_for, request, flash
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, ArrayType, StructType, StructField, StringType
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import udf, col, expr
from bson import ObjectId
from pyspark.sql import Row

app = Flask(__name__)
app.secret_key = "CHANGE ME"

# MongoDB connection settings
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client['music_features']
music_collection = db['audio_features']
user_collection = db['users']  # Collection for users

# Dictionary to store username-password pairs
user_credentials = {}

# Create Spark Session
spark = SparkSession.builder \
    .appName("LSH_NearestNeighbor") \
    .getOrCreate()

# Define the schema including 'features' and 'filename' columns
schema = StructType([
    StructField("features", ArrayType(DoubleType()), nullable=False),
    StructField("filename", StringType(), nullable=False)
])

# Read data from MongoDB collection with the specified schema
df = spark.read.format("mongo") \
    .option("uri", "mongodb://localhost:27017/music_features.audio_features") \
    .schema(schema) \
    .load()

# Check if the DataFrame is empty before fitting the scaler
if df.count() > 0:
    # Filter out rows with inconsistent feature dimensions
    df = df.filter(expr("size(features) = 25822"))

    # Define UDF to convert array to dense vector
    to_vector_udf = udf(lambda features: Vectors.dense(features), VectorUDT())
    df = df.withColumn("features_vector", to_vector_udf(col("features")))

    # Apply Min-Max Scaling
    scaler = MinMaxScaler(inputCol="features_vector", outputCol="scaled_features")
    scaler_model = scaler.fit(df)
    scaled_df = scaler_model.transform(df)

    # Train KMeans Clustering Model
    kmeans = KMeans(featuresCol='scaled_features', predictionCol='prediction', k=5)
    kmeans_model = kmeans.fit(scaled_df)
    clustered_df = kmeans_model.transform(scaled_df)

    # Evaluate the Clustering Model using Silhouette Score
    evaluator = ClusteringEvaluator(distanceMeasure="squaredEuclidean", featuresCol="scaled_features", predictionCol="prediction")
    silhouette = evaluator.evaluate(clustered_df)
    print("Silhouette with squared Euclidean distance =", silhouette)
else:
    print("DataFrame is empty. Cannot fit MinMaxScaler.")

@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()

    # Add a base case validation for username and password
    if request.method == "POST":
        uname = request.form["username"]
        password = request.form["password"]

        # Check if the provided username and password match any of the accepted credentials
        user_data = user_collection.find_one({"username": uname, "password": password})
        if user_data:
            session['username'] = uname
            session['user_id'] = str(user_data['_id'])  # Convert ObjectId to string
            return redirect(url_for("home"))
        else:
            flash("Incorrect username or password")
            return render_template("login.html")

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form["username"]
        password = request.form["password"]

        # Check if username already exists
        if user_collection.find_one({"username": uname}):
            flash("Username already exists")
        else:
            # Insert new user credentials into MongoDB
            user_collection.insert_one({"username": uname, "password": password})
            
            flash("Sign up successful! Please login.")
            return redirect(url_for("login"))  # Redirect to login page after successful signup

    return render_template("signup.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        # Retrieve music files from MongoDB
        music_files = [file['filename'] for file in music_collection.find({}, {'filename': 1})]
        return render_template("home.html", username=session['username'], music_files=music_files)
    else:
        return redirect(url_for('login'))
    



@app.route('/home2', methods=['POST'])
def home2():
    if 'username' in session:
        selected_music = request.form.get('music_file')
        if selected_music:
            # Run ML model to get similar tracks
            selected_features_df = df.filter(col("filename") == selected_music).select("features_vector").collect()
            if selected_features_df:
                selected_features = selected_features_df[0][0]
                selected_features_vector = Vectors.dense(selected_features)

                # Predict the cluster for the selected features
                predicted_cluster = kmeans_model.predict(selected_features_vector)

                # Find similar tracks based on the predicted cluster
                similar_tracks = clustered_df.filter(col("prediction") == predicted_cluster).select("filename").collect()
                similar_tracks = [track["filename"] for track in similar_tracks]

                return render_template("home2.html", username=session['username'], selected_music=selected_music, recommendations=similar_tracks)
            else:
                error_message = "No recommended music for the following file!"
                music_files = [file['filename'] for file in music_collection.find({}, {'filename': 1})]
                return render_template("home.html", username=session['username'], music_files=music_files, error_message=error_message)
        else:
            flash("Please select a music file")
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
