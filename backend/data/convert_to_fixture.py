import json

with open("ingredients.json", encoding="utf-8") as f:
    data = json.load(f)

fixture = []
for i, item in enumerate(data, 1):
    fixture.append({
        "model": "recipes.ingredient",
        "pk": i,
        "fields": {
            "name": item["name"],
            "measurement_unit": item["measurement_unit"]
        }
    })

with open("ingredients_fixture.json", "w", encoding="utf-8") as f:
    json.dump(fixture, f, ensure_ascii=False, indent=2)
