#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Daniel Drizhuk, d.drizhuk@gmail.com, 2017


def has_methods(obj, *methods):
    """
    For ducktype testers.
    Tests for methods to exist on objects.
    :param obj:
    :param methods: (variadic)
    :return:
    """
    for method in methods:
        if not hasattr(obj, method) or not callable(getattr(obj, method)):
            return False
    return True


def is_event_interface(obj):
    '''
    Ducktype-tester for `threading.Event` type.
    Returns `True` if object has callable ``set`` and ``is_set``
    :param obj:
    :return: boolean
    '''
    return has_methods(obj, 'set', 'is_set')


def is_condition_interface(obj):
    '''
    Ducktype-tester for `threading.Condition` type.
    Returns `True` if object has callable ``wait``, ``notify``, ``notify_all``, ``acquire`` and ``release``
    :param obj:
    :return: boolean
    '''
    return has_methods(obj, 'wait', 'notify', 'notify_all', 'acquire', 'release')


def is_notifyable(obj):
    '''
    Ducktype-tester for `threading.Condition` or `threading.Event` type.
    :param obj:
    :return: boolean
    '''
    return is_condition_interface(obj) or is_event_interface(obj)


def notify_or_set(obj):
    '''
    Activator for `threading.Condition` or `threading.Event`.
    :param obj:
    '''
    if is_condition_interface(obj):
        obj.acquire()
        obj.notify_all()
        obj.release()
    else:
        obj.set()


def _get_first_of(obj, *args):
    """
    Helper function, returns first existing property of the object that is not None.
    :param obj:
    :param args: variadic, names of the properties
    :return:
    """
    for arg in args:
        if hasattr(obj, arg):
            prop = getattr(obj, arg)
            if prop is not None:
                return prop

    return None


def is_failed(ev):
    """
    Returns failure of the `threading.Event` or `threading.Condition` if they were supplied through the properties of the object.
    If no failure supplied, `None` is returned.
    :param ev: `threading.Event` or `threading.Condition`
    :return:
    """
    error = _get_first_of(ev, 'exception', 'error', 'failure')
    if error is not None:
        return error

    if _get_first_of(ev, 'failed') or not _get_first_of(ev, 'success'):
        return True

    return None


def get_result(ev):
    """
    Returns result of the `threading.Event` or `threading.Condition` if they were supplied through the properties of the object.
    If no result supplied, `None` is returned.
    :param ev: `threading.Event` or `threading.Condition`
    :return:
    """
    return _get_first_of(ev, 'result', 'success')
