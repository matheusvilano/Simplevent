# Copyright 2024 Matheus Vilano
# MIT License

import unittest
from typing import Any

from src.simplevent import *


class TestClass:
    
    def __init__(self, value: Any):
        self._value = value
    
    def on_event_str(self, **kwargs):
        self.value = "None" if kwargs["data"] is None else kwargs["data"]
    
    def on_event_ref_any(self, value: Any):
        self.value = value
    
    def on_event_ref_str(self, value: str):
        self.value = value
    
    def on_event_ref_args(self, *args):  # should cause an error to be raised
        self.value = args[0]
    
    def on_event_ref_kwargs(self, **kwargs):  # should cause an error to be raised
        self.value = kwargs["data"]
    
    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, value: Any) -> None:
        self._value = value


class TestSimplevent(unittest.TestCase):
    
    def test__str_event__len(self):
        test_obj_a = TestClass(value="X")
        test_obj_b = TestClass(value="Y")
        str_event = StrEvent(test_obj_a.on_event_str.__name__, "data")
        self.assertEqual(len(str_event), 0)
        str_event += test_obj_a
        self.assertEqual(len(str_event), 1)
        str_event += test_obj_b
        self.assertEqual(len(str_event), 2)
        str_event -= test_obj_a
        str_event -= test_obj_b
        self.assertEqual(len(str_event), 0)
        self.assertRaises(ValueError, str_event.__sub__, test_obj_a)
    
    def test__str_event__call(self):
        test_obj_a = TestClass(value="X")
        test_obj_b = TestClass(value="Y")
        str_event = StrEvent("on_event_str", "data")
        self.assertEqual(test_obj_a.value, "X")
        self.assertEqual(test_obj_b.value, "Y")
        str_event += test_obj_a
        str_event += test_obj_b
        self.assertRaises(ArgumentCountError, str_event)
        self.assertEqual(test_obj_a.value, "X")
        self.assertEqual(test_obj_b.value, "Y")
        str_event("T")
        self.assertEqual(test_obj_a.value, "T")
        self.assertEqual(test_obj_b.value, "T")
    
    def test__ref_event__len(self):
        ref_event = RefEvent(Any)
        test_obj_a = TestClass(value="X")
        test_obj_b = TestClass(value="Y")
        self.assertEqual(len(ref_event), 0)
        ref_event += test_obj_a.on_event_ref_any
        self.assertEqual(len(ref_event), 1)
        ref_event += test_obj_b.on_event_ref_any
        self.assertEqual(len(ref_event), 2)
        ref_event -= test_obj_a.on_event_ref_any
        ref_event -= test_obj_b.on_event_ref_any
        self.assertEqual(len(ref_event), 0)
        self.assertRaises(NotCallableError, ref_event.__add__, test_obj_a)
    
    def test_ref_event__call(self):
        ref_event = RefEvent(str)
        test_obj_a = TestClass(value="X")
        test_obj_b = TestClass(value="Y")
        self.assertEqual(test_obj_a.value, "X")
        self.assertEqual(test_obj_b.value, "Y")
        ref_event += test_obj_a.on_event_ref_any
        ref_event += test_obj_b.on_event_ref_any
        ref_event("T")
        self.assertEqual(test_obj_a.value, "T")
        self.assertEqual(test_obj_b.value, "T")
