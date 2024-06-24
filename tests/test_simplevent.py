import unittest
from src import simplevent
from test_utils import *


class TestSimplevent(unittest.TestCase):

	test_obj_a1 = TestClassA()
	test_obj_a2 = TestClassA()
	test_obj_b1 = TestClassB()
	test_obj_b2 = TestClassB()

	def test__ref_event_invocation(self):
		test_event = simplevent.RefEvent()
		test_event.add(get_rice)
		test_event.add(get_protein)
		test_event += get_veggies
		test_event += get_dessert
		test_event()
		self.assertEqual(len(test_event), 4)
		test_event -= get_protein
		test_event -= get_dessert
		self.assertEqual(len(test_event), 2)

	def test__ref_event_param_list(self):
		test_event = simplevent.RefEvent(str)
		test_event += get_food
		test_event += get_food_no_type
		test_event += get_food_any_type
		test_event += get_food_sub_type
		test_event(ExtendedStr("Sweets"))  # subclass is ok
		self.assertEqual(len(test_event), 4)
		test_event -= get_food
		self.assertEqual(len(test_event), 3)

	def test__str_event_invocation(self):
		test_event = simplevent.StrEvent("test_event_invoked", ("response",))
		test_a = TestClassA()
		test_event += test_a
		test_event("T")
		self.assertEqual(test_a.response, "T")
		test_event -= test_a
		test_b = TestClassB()
		test_event += test_b
		test_event("T")
		self.assertEqual(test_b.response, "T")
