from abc import ABC as _ABC, abstractmethod as _abstractmethod
from inspect import signature as _signature, Parameter as _Parameter
from re import match as _match
from typing import Callable as _Callable, Any as _Any, Type as _Type, Tuple as _Tuple, List as _List


class Event(_ABC):
	
	@_abstractmethod
	def __init__(self):
		"""
		Constructs a new Event.
		"""
		super().__init__()
		self._subs = []
	
	def __call__(self, *args, **kwargs):
		"""
		What to do when the Event is invoked.
		:param args: Positional arguments.
		:return: No return value, by default.
		"""
		return self.invoke(*args)
	
	def __add__(self, subscriber):
		"""
		Sugar syntax for adding subscribers.
		:param subscriber: The object to subscribe to the Event.
		"""
		self.add(subscriber)
		return self
	
	def __sub__(self, subscriber):
		"""
		Sugar syntax for removing subscribers.
		:param subscriber: The object to unsubscribe to the Event.
		"""
		self.remove(subscriber)
		return self
	
	def __len__(self):
		"""
		Sugar syntax for checking the current amount of subscribers.
		:return: The current amount of subscribers.
		"""
		return len(self._subs)
	
	@_abstractmethod
	def _validate_subscriber(self, subscriber) -> None:
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		:raise: A BaseEventError, if the subscriber is invalid.
		"""
		pass

	@_abstractmethod
	def invoke(self, *args) -> None:
		"""
		Invokes the event, causing all subscribers to handle (respond to) the event.
		:param args: Positional arguments.
		:return: No return value, by default.
		"""
		pass
	
	def add(self, subscriber) -> None:
		"""
		Adds a new subscriber.
		:param subscriber: The new subscriber.
		"""
		self._validate_subscriber(subscriber)
		if subscriber in self._subs:
			return
		self._subs.append(subscriber)
	
	def insert(self, i: int, subscriber) -> None:
		"""
		Inserts a new subscriber (at the specified index).
		:param i: The index where to insert the new subscriber.
		:param subscriber: The new subscriber
		"""
		self._validate_subscriber(subscriber)
		if subscriber in self._subs:
			return
		self._subs.insert(i, subscriber)
	
	def remove(self, subscriber) -> None:
		"""
		Removes a subscriber.
		:param subscriber: The subscriber to remove.
		"""
		self._subs.remove(subscriber)


class StrEvent(Event):
	"""
	An event with non-function objects as subscribers, that stores its own name as a string. Once invoked, an StrEvent
	will query its subscribers for a method of the same name as itself; if valid, the method is immediately called.
	StrEvent does not enforce function signatures, and all arguments (event data) are broadcast via named arguments
	(**kwargs). It is recommended to document the names of the arguments in a docstring.
	"""
	
	_valid_name_regular_expression = r"^[A-Za-z_][A-Za-z0-9_]*$"
	
	def __init__(self, callback: str, *params: str):
		"""
		Constructs a new StrEvent.
		:param callback: The name of the callback function to look for in subscribers. Once invoked, the event will
		query each of its subscribers for a Callable (usually, a function) of this name and attempt to call it.
		:param param_names: The parameters of the event. By default, the event has no parameters.
		"""
		super().__init__()
		if not isinstance(callback, str) or _match(StrEvent._valid_name_regular_expression, callback) is None:
			raise CallbackNameError("Provided callback name is invalid. Must be a valid function name.")
		self._callback = callback
		self._params = params
	
	def invoke(self, *args) -> None:
		"""
		Calls every single current subscriber's callback function, if valid.
		:param args: Unnamed arguments.
		"""
		if len(args) != len(self._params):
			raise ArgumentCountError
		for subscriber in self._subs:
			if subscriber is not None:
				function = getattr(subscriber, self._callback)
				if function is not None and isinstance(function, _Callable):
					kwargs = dict()
					for i, arg in enumerate(args):
						kwargs[self._params[i]] = arg
					function(**kwargs)
	
	def _validate_subscriber(self, subscriber: _Any):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		"""
		pass  # At the moment, any subscriber is valid for NamedEvent objects.
	
	@property
	def callback(self) -> str:
		""":return: The name of this event's callback."""
		return self._callback
	
	@property
	def param_names(self) -> tuple[str, ...]:
		""":return: The names of the parameters of this event."""
		return self._params


class RefEvent(Event):
	"""
	An event with functions (or functors) as subscribers. The expectation is that the subscribed (signed) function
	will always be called successfully. RefEvent provides "soft" type-safety: this means it has some simple type-safety
	such as checking if an argument that is expected to be a string is in fact a string - but more complex checks such
	as checking types in generics (e.g. collections such as tuple, list, or dict) is not supported.
	"""
	
	def __init__(self, *types: type):
		"""
		Constructs a new RefEvent.
		:param param_types: The param types of the event. When calling the event, these types must be obeyed, in order.
		:param force_subscriber_type_safety: Whether to verify the param types of the subscriber. An exception will be
		raised if the param types are mismatched.
		"""
		super().__init__()
		self._types = types
	
	def invoke(self, *args) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Arguments.
		"""
		
		# Amount of parameters
		if len(args) > len(self._types):
			raise ArgumentCountError(f"Too many params in {self.__class__} call. "
			                         f"Expected {len(self._types)} arguments, "
			                         f"but {len(args)} were given.")
		elif len(args) < len(self._types):
			raise ArgumentCountError(f"Too few params in {self.__class__} call. "
			                         f"Expected {len(self._types)} arguments, "
			                         f"but {len(args)} were given.")
		
		# Expected types ("soft" checks)
		for i, arg in enumerate(args):
			if self._types[i] == _Any:  # Any cannot be used with isinstance
				continue
			origin_class = getattr(self._types[i], "__origin__", None)
			if not isinstance(arg, self._types[i] if origin_class is None else origin_class):
				raise ArgumentCountError(f"An argument has the wrong data type: "
				                         f"{type(arg)}, but {type(arg)} was expected.")
		
		# Null checks (null subscribers are NOT removed)
		for subscriber in self._subs:
			if subscriber is not None:
				subscriber(*args)
	
	def _validate_subscriber(self, subscriber: _Callable):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		:raise: A BaseEventError, if the subscriber is invalid.
		"""
		
		# Callable check
		if not isinstance(subscriber, _Callable):
			raise NotCallableError("New subscriber is not a callable.")
		
		signature = _signature(subscriber)
		
		# Block *args and **kwargs
		for param in signature.parameters.values():
			if param.kind == _Parameter.VAR_POSITIONAL:
				raise SignatureMismatchError("New subscriber's param list contains *args. "
				                             "Positional vars are not supported.")
			if param.kind == _Parameter.VAR_KEYWORD:
				raise SignatureMismatchError("New subscriber's param list contains *kwargs. "
				                             "Keyword vars are not supported.")
		
		# Amount of params
		if len(signature.parameters.values()) > len(self._types):
			raise SignatureMismatchError("New subscriber has too many params. "
			                             f"Event expected {len(self._types)} params.")
		elif len(signature.parameters.values()) < len(self._types):
			raise SignatureMismatchError("New subscriber has too few params. "
			                             f"Event expected {len(self._types)} params.")
		
		# Type checks
		for i, param in enumerate(signature.parameters.values()):
			is_type_same = param.annotation == self._types[i]
			is_type_any = param.annotation == param.empty or param.annotation == _Any
			if not is_type_same and not is_type_any:
				raise SignatureMismatchError("A type from 'subscriber' does not match a type from 'event'. "
				                             f"Got {param.annotation} instead of {self._types[i]}.")
	
	@property
	def signature(self) -> _Tuple[_Type, ...]:
		""":return: The signature of the event. When calling the event, this signature must be obeyed."""
		return self._types


class CallbackNameError(ValueError):
	"""Raised when an invalid callback name is specified."""


class NotCallableError(ValueError):
	"""Raised when a new subscriber is not Callable."""


class SignatureMismatchError(RuntimeError):
	"""Happens when a new subscriber's signature does not match the event's signature."""


class ArgumentCountError(RuntimeError):
	"""Raised when an invalid number of arguments is specified during an event invocation (call)."""
