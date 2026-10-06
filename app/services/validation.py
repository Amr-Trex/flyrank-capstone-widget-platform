# script contains business logic for validating data submitted by end-users through a widget


def clean_and_validate_submission_data(widget: dict, data: dict):
    '''
    Validate and clean submission data against the widget's field configuration.
    Returns a tuple: (cleaned_data_dict, list_of_errors)
    '''
    errors = []

    if not isinstance(data, dict):
        return {}, ["data must be an object"]

    cleaned = {}
    fields = widget.get("fields", [])

    for field in fields:
        if not isinstance(field, dict):
            continue

        name = field.get("name")
        if not name:
            continue

        value = data.get(name)
        required = bool(field.get("required", False))

        if required and (value is None or str(value).strip() == ""):
            errors.append(f"{name} is required")
            continue

        if value is None:
            continue

        if not isinstance(value, str):
            errors.append(f"{name} must be a string")
            continue

        value = value.strip()

        if len(value) > 500:
            errors.append(f"{name} is too long")
            continue

        field_type = field.get("type")

        if field_type == "email" and "@" not in value:
            errors.append(f"{name} must be a valid email")
            continue

        cleaned[name] = value

    # unknown fields are ignored on purpose.
    # the widget only accepts fields defined in its configuration.
    return cleaned, errors