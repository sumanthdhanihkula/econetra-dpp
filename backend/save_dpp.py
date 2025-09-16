from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Or MongoDB Atlas URL
db = client["dpp_database"]  # Database name
collection = db["products"]  # Collection name

# Example DPP JSON
dpp_data = {
    "product_id": "12345",
    "name": "Eco-Friendly Chair",
    "material": "Bamboo",
    "origin": "India",
    "expiry_date": "2030-12-31"
}

# Insert into MongoDB
collection.insert_one(dpp_data)
print("DPP saved to MongoDB!")
