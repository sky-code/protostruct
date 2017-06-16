import pytest

from example_pb2 import StructContainer


def test_empty_list_value_error():
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_list': []}
    items = list(dict_val.items())
    key = items[0][0]
    struct_list = struct_val.get_or_create_list(key)

    # will fail here
    empty_list = struct_val[key]
    assert list(empty_list) == []


def test_empty_dict_value_error():
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_dict': {}}
    items = list(dict_val.items())
    key = items[0][0]
    struct_dict = struct_val.get_or_create_struct(key)

    # will fail here
    empty_dict = struct_val[key]
    assert dict(empty_dict.fields) == {}


def test_empty_list_hack():
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_list': []}
    items = list(dict_val.items())
    key = items[0][0]
    struct_list = struct_val.get_or_create_list(key)
    # hack for fix ValueError 'Value not set'
    struct_list.append(1)
    struct_list.values.pop(0)

    # ok now try to get empty list from struct
    empty_list = struct_val[key]
    assert list(empty_list) == []


def test_empty_dict_hack():
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_dict': {}}
    items = list(dict_val.items())
    key = items[0][0]
    struct_dict = struct_val.get_or_create_struct(key)
    # hack ValueError 'Value not set'
    struct_dict['k'] = 'v'
    del struct_dict.fields['k']

    # ok now try to get empty list from struct
    empty_dict = struct_val[key]
    assert dict(empty_dict.fields) == {}


def test_empty_list_unpack_value_error():
    """version with bug"""
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_list': []}
    update_from_dict_bug(struct_val, dict_val)

    unpack_dict = update_from_struct_bug({}, struct_val)
    assert len(unpack_dict) == 1
    first = list(unpack_dict.items())[0]
    assert first[0] == 'empty_list'
    assert list(first[1]) == []


def test_empty_dict_unpack_value_error():
    """version with bug"""
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_dict': {}}
    update_from_dict_bug(struct_val, dict_val)

    unpack_dict = update_from_struct_bug({}, struct_val)
    assert len(unpack_dict) == 1
    first = list(unpack_dict.items())[0]
    assert first[0] == 'empty_dict'
    assert dict(first[1]) == {}


def test_empty_list_unpack():
    """version with fix"""
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_list': []}
    update_from_dict(struct_val, dict_val)

    unpack_dict = update_from_struct_bug({}, struct_val)
    assert len(unpack_dict) == 1
    first = list(unpack_dict.items())[0]
    assert first[0] == 'empty_list'
    assert list(first[1]) == []


def test_empty_dict_unpack():
    """version with fix"""
    container = StructContainer()
    struct_val = container.data
    dict_val = {'empty_dict': {}}
    update_from_dict(struct_val, dict_val)

    unpack_dict = update_from_struct_bug({}, struct_val)
    assert len(unpack_dict) == 1
    first = list(unpack_dict.items())[0]
    assert first[0] == 'empty_dict'
    assert dict(first[1]) == {}


def update_from_struct_bug(dict_value, struct):
    """recursive function that copy items from struct into dict_value

    Args:
        dict_value: dict or dict-like object that will be updated
        struct: protobuf Struct object used as source for update

    Returns:
        updated dict
    """
    if isinstance(dict_value, dict):
        for key, value in struct.fields.items():
            which_value = value.WhichOneof('kind')
            if which_value == 'struct_value':
                val = {}
                dict_value[key] = val
                update_from_struct_bug(val, struct[key])
            elif which_value == 'list_value':
                val = []
                dict_value[key] = val
                update_from_struct_bug(val, struct[key])
            else:
                dict_value[key] = struct[key]
    elif isinstance(dict_value, list):
        for index, value in enumerate(struct.values):
            which_value = value.WhichOneof('kind')
            if which_value == 'struct_value':
                val = {}
                dict_value.append(val)
                update_from_struct_bug(val, value)
            elif which_value == 'list_value':
                val = []
                dict_value.append(val)
                update_from_struct_bug(val, value)
            else:
                dict_value.append(struct[index])
    return dict_value


def update_from_dict_bug(struct, dict_value):
    """recursive function that copy items from dict_value into struct

    this implementation contains the bug with empty list value and empty struct value

    Args:
        struct: protobuf Struct object
        dict_value: dict or dict-like object

    Returns:
        None, result is side effects on struct argument
    """
    if isinstance(dict_value, dict):
        for key, val in dict_value.items():
            if isinstance(val, dict):
                inner_struct = struct.get_or_create_struct(key)
                update_from_dict_bug(inner_struct, val)
            elif isinstance(val, list):
                inner_struct = struct.get_or_create_list(key)
                update_from_dict_bug(inner_struct, val)
            else:
                struct[key] = val
    elif isinstance(dict_value, list):
        for val in dict_value:
            if isinstance(val, dict):
                inner_struct = struct.add_struct()
                update_from_dict_bug(inner_struct, val)
            elif isinstance(val, list):
                inner_struct = struct.add_list()
                update_from_dict_bug(inner_struct, val)
            else:
                struct.append(val)


def update_from_struct(dict_value, struct):
    """recursive function that copy items from struct into dict_value

    Args:
        dict_value: dict or dict-like object that will be updated
        struct: protobuf Struct object used as source for update

    Returns:
        updated dict
    """
    if isinstance(dict_value, dict):
        for key, value in struct.fields.items():
            which_value = value.WhichOneof('kind')
            if which_value == 'struct_value':
                val = {}
                dict_value[key] = val
                update_from_struct(val, struct[key])
            elif which_value == 'list_value':
                val = []
                dict_value[key] = val
                update_from_struct(val, struct[key])
            else:
                dict_value[key] = struct[key]
    elif isinstance(dict_value, list):
        for index, value in enumerate(struct.values):
            which_value = value.WhichOneof('kind')
            if which_value == 'struct_value':
                val = {}
                dict_value.append(val)
                update_from_struct(val, value)
            elif which_value == 'list_value':
                val = []
                dict_value.append(val)
                update_from_struct(val, value)
            else:
                dict_value.append(struct[index])
    return dict_value


def update_from_dict(struct, dict_value):
    """recursive function that copy items from dict_value into struct

    this implementation contains the hack for empty list value and empty struct value serialization

    Args:
        struct: protobuf Struct object
        dict_value: dict or dict-like object

    Returns:
        None, result is side effects on struct argument
    """
    if isinstance(dict_value, dict):
        _force_add_remove_item = True
        for key, val in dict_value.items():
            _force_add_remove_item = False
            if isinstance(val, dict):
                inner_struct = struct.get_or_create_struct(key)
                update_from_dict(inner_struct, val)
            elif isinstance(val, list):
                inner_struct = struct.get_or_create_list(key)
                update_from_dict(inner_struct, val)
            else:
                struct[key] = val
        if _force_add_remove_item is True:
            # hack for fix ValueError 'Value not set'
            struct['k'] = 'v'
            del struct.fields['k']
    elif isinstance(dict_value, list):
        _force_add_remove_item = True
        for val in dict_value:
            _force_add_remove_item = False
            if isinstance(val, dict):
                inner_struct = struct.add_struct()
                update_from_dict(inner_struct, val)
            elif isinstance(val, list):
                inner_struct = struct.add_list()
                update_from_dict(inner_struct, val)
            else:
                struct.append(val)
        if _force_add_remove_item is True:
            # hack for fix ValueError 'Value not set'
            struct.append(0)
            struct.values.pop(0)
