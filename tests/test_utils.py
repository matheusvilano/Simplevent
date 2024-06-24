from typing import Any


class TestClassA(object):
	
	def __init__(self):
		self.response: str | None = None
	
	def test_event_invoked(self, **kwargs):
		self.response = "A" if kwargs["response"] is None else kwargs["response"]


class TestClassB(object):
	
	def __init__(self):
		self.response: str | None = None
	
	def test_event_invoked(self, **kwargs):
		self.response = "B" if kwargs["response"] is None else kwargs["response"]


class ExtendedStr(str):
	pass


def get_veggies():
	return "Veggies!"


def get_protein():
	print("Protein!")


def get_dessert():
	print("Dessert!")


def get_rice():
	print("Rice!")


def get_food(food_name: str):
	print(f"{food_name}!")


def get_food_any_type(food_name: Any):
	print(f"{food_name}!")


def get_food_no_type(food_name):
	print(f"{food_name}!")


def get_food_sub_type(food_name: ExtendedStr):
	print(f"{food_name}!")
