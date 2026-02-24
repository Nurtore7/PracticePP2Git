import json
import os

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "..", "sample-data.json")

with open(file_path, "r") as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print("DN                                                 Description          Speed    MTU")
print("-" * 80)

for item in data["imdata"]:
    attrs = item["l1PhysIf"]["attributes"]

    dn = attrs["dn"]
    speed = attrs["speed"]
    mtu = attrs["mtu"]

    print(dn, " " * (55 - len(dn)), speed, "   ", mtu)