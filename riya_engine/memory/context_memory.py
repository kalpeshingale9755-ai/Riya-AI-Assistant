_last_entity = None



def set_last_entity(entity: str):
    global _last_entity

    if entity:
        _last_entity = entity
        print(f"[Context] Last entity set to: {entity}")


def get_last_entity():
    return _last_entity



def clear_context():
    global _last_entity
    _last_entity = None
    