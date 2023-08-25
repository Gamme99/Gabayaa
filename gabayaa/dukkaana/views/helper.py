import json


def calculate_item_count(cart):
    item_count = 0
    for item_id, item in cart.items():
        quantity = item.get('quantity')
        item_count += quantity

    # print("total: ", item_count)
    return item_count


def convertToDict(cart_json):
    if isinstance(cart_json, str):
        cart = json.loads(cart_json)
    else:
        cart = cart_json
    return cart
