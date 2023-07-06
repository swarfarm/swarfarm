from math import trunc
from datetime import datetime
from django.core.mail import mail_admins

from django.utils import timezone


def slice_records(qs, *args, **kwargs):
    report_timespan = kwargs.get('report_timespan')
    minimum_count = kwargs.get('minimum_count')
    maximum_count = kwargs.get('maximum_count')
    start_date = kwargs.get('start_date')
    end_date = kwargs.get('end_date')
    now = timezone.now()

    if start_date:
        if isinstance(start_date, str):
            start_date = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
        elif not timezone.is_aware(start_date):
            start_date = timezone.make_aware(start_date)
    if end_date:
        if isinstance(end_date, str):
            end_date = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
        elif not timezone.is_aware(end_date):
            end_date = timezone.make_aware(end_date)
        end_date = min(end_date, now)

    if start_date and end_date and (end_date - start_date).days > report_timespan.days:
        start_date = end_date - report_timespan

    if minimum_count and maximum_count:
        raise ValueError('Cannot use minimum_count and maximum_count at the same time.')

    if qs.count() == 0:
        return qs

    if start_date and end_date:
        result = qs.filter(timestamp__gte=start_date, timestamp__lte=end_date)
    elif report_timespan:
        result = qs.filter(timestamp__gte=now - report_timespan)
    else:
        result = qs

    if not (start_date and end_date) and (minimum_count or maximum_count):
        num_records = result.count()

        if num_records > 0:
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
    transform = kwargs.get('transform')

    for item in data:
        if name_key is None:
            # Find the first key that is not the value_key and use that
            for key in item.keys():
                if key != value_key:
                    name_key = key
                    break

        try:
            if transform:
                dict_data[transform[item[name_key]]] = item[value_key]
            else:
                dict_data[item[name_key]] = item[value_key]
        except KeyError as e:
            continue

    return dict_data


def round_timedelta(input, to_nearest, direction='up'):
    if direction == 'up':
        return to_nearest * trunc(input / to_nearest) + to_nearest
    else:
        return to_nearest * trunc(input / to_nearest)
