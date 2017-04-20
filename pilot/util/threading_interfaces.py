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
