import unittest
from src import simplevent
from test_utils import get_food, get_rice, get_protein, get_veggies, get_dessert, TestClassA, TestClassB


class TestSimplevent(unittest.TestCase):

	test_obj_a1 = TestClassA()
	test_obj_a2 = TestClassA()
	test_obj_b1 = TestClassB()
	test_obj_b2 = TestClassB()

	def test_signed_event_invocation(self):
		test_event: simplevent.SignedEvent = simplevent.SignedEvent(return_from_subscribers=True)
		test_event.add(get_rice)
		test_event.add(get_protein)
		test_event += get_veggies
		test_event += get_dessert
		return_values: list = test_event()
		self.assertListEqual(return_values, ["Rice!", "Protein!", "Veggies!", "Dessert!"])
		test_event -= get_protein
		test_event -= get_dessert
		return_values = test_event.invoke()
		self.assertListEqual(return_values, ["Rice!", "Veggies!"])

	def test_signed_event_subscription_with_any_param_amount(self):
		test_event: simplevent.SignedEvent = simplevent.SignedEvent(return_from_subscribers=True)
		test_event.add(get_rice)
		test_event.add(get_protein)
		test_event += get_veggies
		test_event += get_dessert
		self.assertEqual(len(test_event), 4)
		test_event -= get_rice
		test_event -= get_veggies
		self.assertEqual(len(test_event), 2)

	def test_signed_event_subscription_with_fixed_param_amount(self):
		test_event_one_param: simplevent.SignedEvent = simplevent.SignedEvent(amount_of_params=1)
		test_event_no_param: simplevent.SignedEvent = simplevent.SignedEvent(amount_of_params=0)
		self.assertRaises(simplevent.IncorrectNumberOfParamsError, lambda: test_event_one_param.add(get_dessert))
		self.assertRaises(simplevent.IncorrectNumberOfParamsError, lambda: test_event_no_param.add(get_food))

	def test_named_event_invocation(self):
		test_event = simplevent.NamedEvent("test_event_invoked", allow_duplicate_subscribers=False)
		test_event += self.test_obj_b1
		test_event()
		self.assertEqual(self.test_obj_b1.response, "B")
		test_event.remove(self.test_obj_b1)
		test_event.add(self.test_obj_b2)
		test_event.invoke()
		self.assertEqual(self.test_obj_b2.response, "B")

	def test_named_event_subscription_without_duplicate_subs(self):
		test_event = simplevent.NamedEvent("test_event_invoked", allow_duplicate_subscribers=False)
		test_event += self.test_obj_b1
		self.assertNotEqual(getattr(test_event._subs[0], test_event.name), None)

	def test_named_event_subscription_with_duplicate_subs(self):
		test_event = simplevent.NamedEvent("test_event_invoked", allow_duplicate_subscribers=True)
		test_event.add(self.test_obj_a1)
		self.assertEqual(len(test_event), 1)
		test_event += self.test_obj_a2
		self.assertEqual(len(test_event), 2)
		test_event -= self.test_obj_a1
		test_event.remove(self.test_obj_a2)
		self.assertEqual(len(test_event), 0)
