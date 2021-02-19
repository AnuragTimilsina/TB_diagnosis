import gdown
import subprocess
import sys
import os

base = os.path.dirname(os.path.realpath(__file__))

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

with open("requirements.txt") as requirements:
    requirements = requirements.readlines()[0]
    install(requirements)


print("Downloading model:")
url = 'https://drive.google.com/uc?id=1oBflqba21kBBhalH5sGO8ScPzmsxWu_G'
output = os.path.join(base, "./models/tb_diagnosis_model.h5")
gdown.download(url, output, quiet=False)
print("Model downloaded")


