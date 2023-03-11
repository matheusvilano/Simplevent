def get_veggies():
	return "Veggies!"


def get_protein():
	return "Protein!"


def get_dessert():
	return "Dessert!"


def get_rice():
	return "Rice!"


def get_food(food_name: str):
	return f"{food_name}!"


class TestClassA(object):

	def __init__(self):
		self.response: str | None = None

	def test_event_invoked(self):
		self.response = "A"


class TestClassB(object):

	def __init__(self):
		self.response: str | None = None

	def test_event_invoked(self):
		self.response = "B"
