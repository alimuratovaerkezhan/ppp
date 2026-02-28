import json
with open("sample-data.json", "r") as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)

print(f"{'DN':<50} {'Description':<20} {'Speed':<8} {'MTU':<6}")
print("-" * 50 + " -------------------- ------ ------")

for item in data["imdata"]:
    interface = item["l1PhysIf"]["attributes"]

    dn = interface.get("dn", "")
    description = interface.get("descr", "")
    speed = interface.get("speed", "")
    mtu = interface.get("mtu", "")

    print(f"{dn:<50} {description:<20} {speed:<8} {mtu:<6}")