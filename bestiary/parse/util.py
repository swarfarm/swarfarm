def update_bestiary_obj(model, com2us_id, defaults):
    obj, created = model.objects.get_or_create(com2us_id=com2us_id, defaults=defaults)

    if created:
        print(f'!!! Created new {model.__name__} {com2us_id}')
    else:
        # Compare parsed values to existing object
        updated = False

        for field, parse_value in defaults.items():
            current_value = getattr(obj, field)
            if current_value != parse_value:
                print(f'Updating {field} for {com2us_id} from `{current_value}` to `{parse_value}`.')
                setattr(obj, field, parse_value)
                updated = True

        if updated:
            obj.save()

    return obj
