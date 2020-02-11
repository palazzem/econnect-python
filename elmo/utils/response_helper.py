def slice_list(items, names, key):
    """Slice `items` list into two lists, using the `key` argument to define which
    item belongs to which list. `key` is used on each item and it must be a boolean value.
    During the slice, `names` list values are merged so that every items will include
    relevant data. An `Index` key is used to find the right name for the given `item`.

    This function is a helper to reduce code duplication, and is not meant to be generic.

    Args:
        items: The list that is sliced into two lists.
        names: The list that contains data that should be merged with `items`.
        key: The key that is used to decide on which list `item` should be put. The
            item is accesed as a dict, and the value must be a boolean.
    Returns:
        Two lists where the first list contains only items which key was `True`, while
        the second one contains items which key was `False`.
    """
    list_active = []
    list_not_active = []
    for item in items:
        try:
            # Not all items may have a mapped name
            name = names[item["Index"]]
        except IndexError:
            name = "Unknown"

        entry = {"id": item["Id"], "index": item["Index"], "name": name}
        if item[key]:
            list_active.append(entry)
        else:
            list_not_active.append(entry)

    return list_active, list_not_active
