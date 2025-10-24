from pymongo import MongoClient

uri = "mongodb+srv://ismasohail_user:l5waJh3lij2SsnJd@cluster0.e3wct64.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Force connection on a request as the connect=True parameter of MongoClient seems to be useless here
    client.admin.command('ping')
    print("✅ Connected successfully to MongoDB Atlas!")

    print("📚 Databases available:", client.list_database_names())

except Exception as e:
    print("❌ Connection failed:", e)
