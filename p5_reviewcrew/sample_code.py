
import os
import json

password = "hunter2"          # hardcoded secret
API_URL = "http://api.example.com"   # http not https

def get_user(id):             # no type hints
    data = []
    for i in range(100):      # unused loop variable
        x = i * 2
    result = json.loads('{"name": "test"}')
    return result

def save_to_file(filename, content):
    f = open(filename, 'w')   # file handle never closed
    f.write(content)

class dataProcessor:          # class name not PascalCase
    def __init__(self):
        self.items = []

    def process(self, items):
        self.items = items
        for item in self.items:
            print(item)       # print in production code
