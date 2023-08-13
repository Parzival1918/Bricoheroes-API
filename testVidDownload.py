from deta import Deta

# Initialize with a Project Key from DetaBaseKey.txt
with open("DetaBaseKey.txt") as f:
    key = f.read()

deta = Deta(key)
db = deta.Drive("bricoheroes-drive")