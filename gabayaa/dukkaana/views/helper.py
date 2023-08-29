import json


def calculate_item_count(cart):
    item_count = 0
    for item_id, item in cart.items():
        quantity = item.get('quantity')
        item_count += quantity

    # print("total: ", item_count)
    return item_count


def convertToDict(cart_json):
    cart = {}
    if isinstance(cart_json, str):
        # print("isinstance")
        cart = json.loads(cart_json)
    else:
        # print("is not, its dictionary")
        cart = cart_json
    return cart
