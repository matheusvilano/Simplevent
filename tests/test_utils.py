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
