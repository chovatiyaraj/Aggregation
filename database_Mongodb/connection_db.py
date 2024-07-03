import pymongo

# client = pymongo.MongoClient("mongodb://localhost:27017/")
client = pymongo.MongoClient("mongodb+srv://vaibhav:09WRQ6742v38LFjh@manishbhai-9262a799.mongo.ondigitalocean.com/admin?replicaSet=manishbhai&tls=true&authSource=admin")

print("Client :->",client)


investment_db = client['investment']





