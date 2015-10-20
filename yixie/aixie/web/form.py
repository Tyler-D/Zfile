#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Input(object):
    def __init__(self, name, *validators):
        self.name = name
        self.validators = validators
        self.note = None

    def validate(self, value):
        for v in self.validators:
            if not v.valid(value):
                self.note = v.msg
                return False
            return True

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def get_note(self):
        return self.note

class Validator:
    def __deepcopy__(self, memo): return copy.copy(self)
    def __init__(self): pass

class regexp(Validator):
    def __init__(self, rexp, msg):
        self.rexp = re.compile(rexp)
        self.msg = msg
    def valid(self, value):
        return bool(self.rexp.match(value))
