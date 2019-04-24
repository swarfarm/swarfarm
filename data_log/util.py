
def floor_to_nearest(num, multiple_of):
    return num - num % multiple_of


def round_to_nearest(num, multiple_of):
    return multiple_of * round(num / multiple_of)


def ceil_to_nearest(num, multiple_of):
    return num + multiple_of - num % multiple_of


def replace_value_with_choice(data, attribute, choices):
    """
    :param data: list of dictionaries
    :param attribute: the dictionary key to replace value with choice string
    :param choices: iterable of (value, string) as defined in the model field
    :return: list of dictionaries
    """
    choice_dict = dict(choices)
    for item in data:
        item[attribute] = choice_dict.get(item[attribute], item[attribute])

    return data
