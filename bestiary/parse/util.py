import difflib


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
                if isinstance(current_value, str):
                    # Display a diff
                    print(f'Updating {field} for {com2us_id}')
                    for line in difflib.ndiff([current_value], [parse_value]):
                        print(line)
                else:
                    print(f'Updating {field} for {com2us_id} from `{current_value}` to `{parse_value}`.')
                setattr(obj, field, parse_value)
                updated = True

        if updated:
            obj.save()

    return obj


def show_diff(seqm):
    """Unify operations between two compared strings
seqm is a difflib.SequenceMatcher instance whose a & b are strings"""
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("{+" + seqm.b[b0:b1] + "+}")
        elif opcode == 'delete':
            output.append("{-" + seqm.a[a0:a1] + "-}")
        elif opcode == 'replace':
            output.append("<del>" + seqm.a[a0:a1] + "</del><ins>" + seqm.b[b0:b1] + "</ins>")
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)