from utils.data_loader import (
    load_listings,
    get_example_wardrobe,
    get_empty_wardrobe,
)

print(load_listings()[:2])

print("\nExample Wardrobe:")
print(get_example_wardrobe())

print("\nEmpty Wardrobe:")
print(get_empty_wardrobe())
