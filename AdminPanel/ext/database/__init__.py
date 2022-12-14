from pymongo import MongoClient
from bunnet import init_bunnet
from AdminPanel.ext.models.jewell import *

client = MongoClient("mongodb://localhost:27017")

init_bunnet(database=client.jewell, document_models=[User])
