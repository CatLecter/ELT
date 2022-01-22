def list_to_tuple(list_id: list) -> tuple:
    piece = []
    for _ in list_id:
        _id = str(*_)
        piece.append(_id)
    return tuple(piece)
