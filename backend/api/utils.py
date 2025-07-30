def generate_shopping_cart_content(ingredients):
    lines = []
    for item in ingredients:
        line = (
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) — "
            f"{item['total_amount']}"
        )
        lines.append(line)
    return '\n'.join(lines)
