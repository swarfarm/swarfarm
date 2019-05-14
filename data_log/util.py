
def floor_to_nearest(num, multiple_of):
    return num - num % multiple_of


def round_to_nearest(num, multiple_of):
    return multiple_of * round(num / multiple_of)


def ceil_to_nearest(num, multiple_of):
    return num + multiple_of - num % multiple_of


def replace_value_with_choice(data, replacements):
    """
    :param data: list of dictionaries
    :param replacements: dict of {attribute: choices} to replace
    :return: list of dictionaries
    """
    for attribute, choices in replacements.items():
        choice_dict = dict(choices)
        for item in data:
            if attribute in item:
                item[attribute] = choice_dict.get(
                    item[attribute],
                    item[attribute] if item[attribute] is not None else 'None'
                )

    return data


def transform_to_dict(data, value_key='count'):
    dict_data = {}
    name_key = None

    for item in data:
        if name_key is None:
            # Find the first key that is not the value_key and use that
            for key in item.keys():
                if key != value_key:
                    name_key = key
                    break

        dict_data[item[name_key]] = item[value_key]

    return dict_data
