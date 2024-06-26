import unittest
from src.simplevent.simplevent import *
from typing import Any


class TestClass:
	
	def __init__(self, value: Any):
		self.value = value
	
	def on_event(self, **kwargs):
		self.value = "None" if kwargs["data"] is None else kwargs["data"]


class TestSimplevent(unittest.TestCase):

	def test__str_event(self):
		str_event = StrEvent("on_event", "data")
		test_obj_a = TestClass(value="X")
		test_obj_b = TestClass(value="Y")
		self.assertEqual(len(str_event), 0)
		self.assertEqual(test_obj_a.value, "X")
		self.assertEqual(test_obj_b.value, "Y")
		str_event += test_obj_a
		self.assertEqual(len(str_event), 1)
		str_event += test_obj_b
		self.assertEqual(len(str_event), 2)
		self.assertRaises(EventCallParameterListMismatchError, str_event)
		self.assertEqual(test_obj_a.value, "X")
		self.assertEqual(test_obj_b.value, "Y")
		str_event("T")
		self.assertEqual(test_obj_a.value, "T")
		self.assertEqual(test_obj_b.value, "T")
	
	def test__ref_event(self):
		ref_event
		test_obj_a = TestClass(value="X")
		test_obj_b = TestClass(value="Y")
