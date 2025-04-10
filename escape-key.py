import json

with open("tribal-pride-449015-v3-2ed492bf12d3.json", "r") as f:

    data = json.load(f)
    raw_key = data["private_key"]

# Escape newlines
escaped_key = raw_key.replace("\n", "\\n")

print("Paste this into secrets.toml:\n")
print(f'private_key = "{escaped_key}"')
