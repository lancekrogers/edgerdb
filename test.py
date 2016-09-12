from edgerdb import EdgerDb

edger = EdgerDb()

try:
        edger.create_and_load()
except Exception as e:
        print(e)
