from abc import ABC as _ABC, abstractmethod as _abstractmethod
from inspect import signature as _signature
from re import match as _match
from typing import Callable as _Callable, Any as _Any, Type as _Type


class Event(_ABC):
	
	@_abstractmethod
	def __init__(self):
		"""
		Constructs a new Event.
		"""
		super().__init__()
		self._subs: list = []
	
	@_abstractmethod
	def __call__(self, *args, **kwargs):
		"""
		What to do when the Event is invoked.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		pass
	
	def __add__(self, subscriber):
		"""
		Sugar syntax for adding subscribers.
		:param subscriber: The object to subscribe to the Event.
		"""
		self._validate_subscriber(subscriber)
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
	
	def invoke(self, *args) -> None:
		"""
		Invokes the event, causing all subscribers to handle (respond to) the event.
		:param args: Positional arguments.
		:return: No return value, by default.
		"""
		return self.__call__(*args)
	
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
			raise InvalidEventNameError
		self._callback = callback
		self._params = params
	
	def __call__(self, *args) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		if len(args) != len(self._params):
			raise EventCallParameterListMismatchError
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
		self._param_types = types
	
	def __call__(self, *args) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		
		# Amount of parameters
		if len(args) > len(self._param_types):
			raise EventCallParameterListMismatchError(f"Too many params in {self.__class__} call. "
			                                          f"Expected {len(self._param_types)} arguments, "
			                                          f"but {len(args)} were given.")
		elif len(args) < len(self._param_types):
			raise EventCallParameterListMismatchError(f"Too few params in {self.__class__} call. "
			                                          f"Expected {len(self._param_types)} arguments, "
			                                          f"but {len(args)} were given.")
		
		# Expected types ("soft" checks)
		for i, arg in enumerate(args):
			origin_class = getattr(self._param_types[i], "__origin__", None)
			if not isinstance(arg, self._param_types[i] if origin_class is None else origin_class):
				raise EventCallParameterListMismatchError(f"An argument has the wrong data type: "
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
			raise SubscriberIsNotCallableError("New subscriber is not a callable.")
		
		# Amount of params
		subscriber_signature = _signature(subscriber)
		if len(subscriber_signature.parameters.values()) > len(self._param_types):
			raise SubscriberSignatureMismatchError("New subscriber has too many params. "
			                                       f"Event expected {len(self._param_types)} params.")
		elif len(subscriber_signature.parameters.values()) < len(self._param_types):
			raise SubscriberSignatureMismatchError("New subscriber has too few params. "
			                                       f"Event expected {len(self._param_types)} params.")
		
		# Type checks
		for i, param in enumerate(subscriber_signature.parameters.values()):
			is_type_same = param.annotation == self._param_types[i]
			is_type_any = param.annotation == param.empty and param.annotation == _Any
			if not is_type_same and not is_type_any:
				raise SubscriberSignatureMismatchError("A type from 'subscriber' does not match a type from 'event'. "
				                                       f"Got {param.annotation} instead of {self._param_types[i]}.")
	
	@property
	def signature(self) -> tuple[_Type, ...]:
		""":return: The signature of the event. When calling the event, this signature must be obeyed."""
		return self._param_types


class _BaseEventError(BaseException):
	"""The base class for all errors in Simplevent."""


class InvalidEventNameError(_BaseEventError):
	"""Raised when an invalid event name is specified. Examples: value is not a string; value is an empty string."""


class SubscriberSignatureMismatchError(_BaseEventError):
	"""Happens when a new subscriber's signature does not match the event's signature."""


class EventCallParameterListMismatchError(_BaseEventError):
	"""Raised when an invalid number of parameters is specified when an event is called."""


class SubscriberIsNotCallableError(_BaseEventError):
	"""Raised when a new subscriber is not Callable."""
