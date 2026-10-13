
from roboflow import Roboflow
rf = Roboflow(api_key="5ft3mPtul6yIccwiGFx3")
project = rf.workspace("abdul-hameed-pgqrk").project("hardhat-safetyvest-aigr8")
version = project.version(1)
dataset = version.download("yolov8")