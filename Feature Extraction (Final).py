import os
import numpy as np
import librosa
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['music_features']
collection = db['audio_features']

# Function to extract features from audio file
def extract_features(audio_file):
    try:
        y, sr = librosa.load(audio_file)  # Load audio file
        mfccs = librosa.feature.mfcc(y=y, sr=sr)  # Extract MFCCs
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]  # Extract spectral centroid
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]  # Extract zero-crossing rate
        
        # Ensure all arrays have the same number of dimensions
        mfccs = mfccs.flatten()
        spectral_centroid_mean = np.mean(spectral_centroid)
        zero_crossing_rate_mean = np.mean(zero_crossing_rate)
        
        # Concatenate features
        features = np.concatenate([mfccs, [spectral_centroid_mean], [zero_crossing_rate_mean]])
        
        # Reshape features to 2D array
        features = features.reshape(-1, 1)
        
        # Normalization/Standardization
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        return features_scaled.flatten()  # Return normalized/standardized features
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return None

# Iterate through folders and process audio files
base_folder = r'C:\Users\User\Desktop\BDA\Project\New folder'
folders = ['000', '001', '002', '003', '004', '005', '006', '007', '008', '009', '010']

for folder in folders:
    folder_path = os.path.join(base_folder, folder)
    audio_files = os.listdir(folder_path)
    
    for audio_file in audio_files:
        audio_file_path = os.path.join(folder_path, audio_file)
        
        if audio_file.endswith(".mp3"):
            # Extract features
            features = extract_features(audio_file_path)
            
            if features is not None:
                # Store features in MongoDB
                doc = {
                    "folder": folder,
                    "filename": audio_file,
                    "features": features.tolist()
                }
                collection.insert_one(doc)

print("Feature extraction, normalization, and storage complete.")
