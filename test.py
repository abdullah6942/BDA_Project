import os
import librosa
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['your_database_name']
collection = db['your_collection_name']

# Function to extract features from audio files
def extract_features(audio_files):
    for audio_file in audio_files:
        try:
            # Load audio file and extract features
            y, sr = librosa.load(audio_file)
            mfccs = librosa.feature.mfcc(y=y, sr=sr)
            
            # Normalize or standardize mfccs if needed
            # Apply dimensionality reduction if needed

            # Insert features into MongoDB
            data = {'audio_file': audio_file, 'features': mfccs.tolist()}
            collection.insert_one(data)
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")

# Iterate through folders and process audio files in batches
root_folder = r'F:\BDA_Project\fma_medium'  # Updated path
batch_size = 10  # Adjust batch size based on memory constraints
for folder_name in os.listdir(root_folder):
    folder_path = os.path.join(root_folder, folder_name)
    if os.path.isdir(folder_path):
        audio_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp3')]
        for i in range(0, len(audio_files), batch_size):
            batch = audio_files[i:i+batch_size]
            extract_features(batch)
