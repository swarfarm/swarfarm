from django.utils import timezone


def slice_records(qs, *args, **kwargs):
    report_timespan = kwargs.get('report_timespan')
    minimum_count = kwargs.get('minimum_count')
    maximum_count = kwargs.get('maximum_count')

    if minimum_count and maximum_count:
        raise ValueError('Cannot use minimum_count and maximum_count at the same time.')

    if qs.count() == 0:
        return qs

    if report_timespan:
        result = qs.filter(timestamp__gte=timezone.now() - report_timespan)
    else:
        result = qs

    if minimum_count or maximum_count:
        num_records = result.count()

        if minimum_count and num_records < minimum_count:
            temp_slice = qs[:minimum_count]
            earliest_record = temp_slice[temp_slice.count() - 1]
            result = qs.filter(timestamp__gte=earliest_record.timestamp)

        if maximum_count and num_records > maximum_count:
            temp_slice = qs[:maximum_count]
            earliest_record = temp_slice[temp_slice.count() - 1]
            result = qs.filter(timestamp__gte=earliest_record.timestamp)

    return result


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


def transform_to_dict(data, value_key='count', **kwargs):
    dict_data = {}
    name_key = kwargs.get('name_key')

    for item in data:
        if name_key is None:
            # Find the first key that is not the value_key and use that
            for key in item.keys():
                if key != value_key:
                    name_key = key
                    break

        dict_data[item[name_key]] = item[value_key]

    return dict_data
