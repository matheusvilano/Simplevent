from abc import ABC as _ABC, abstractmethod as _abstractmethod
from inspect import signature as _signature
from re import match as _match
from typing import Callable as _Callable, Type as _Type, Any as _Any


class Event(_ABC):

	@_abstractmethod
	def __init__(self):
		"""
		Constructs a new Event.
		"""
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

	def __init__(self, event_name: str, param_names: tuple[str, ...] = ()):
		"""
		Constructs a new StrEvent.
		:param event_name: The name of the event. This is also the name of the callback function to look for in the
		event's subscribers.
		:param param_names: The parameters of the event. By default, the event has no parameters.
		"""
		super().__init__()
		if not isinstance(event_name, str) or _match(StrEvent._valid_name_regular_expression, event_name) is None:
			raise InvalidEventNameError
		self._name = event_name
		self._param_names = param_names

	def __call__(self, *args) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		if len(args) != len(self._param_names):
			raise EventCallParameterListMismatchError
		for subscriber in self._subs:
			if subscriber is not None:
				function = getattr(subscriber, self._name)
				if function is not None and isinstance(function, _Callable):
					kwargs = dict()
					for i, arg in enumerate(args):
						kwargs[self._param_names[i]] = arg
					function(**kwargs)

	def _validate_subscriber(self, subscriber: _Any):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		"""
		pass  # At the moment, any subscriber is valid for NamedEvent objects.

	@property
	def name(self) -> str:
		""":return: The name of this event."""
		return self._name

	@property
	def param_names(self) -> tuple[str, ...]:
		""":return: The names of the parameters of this event."""
		return self._param_names


class RefEvent(Event):
	"""
	An event with functions (or functors) as subscribers. The expectation is that the subscribed (signed) function
	will always be called successfully. RefEvent provides "soft" type-safety.
	"""

	def __init__(self, param_types: tuple[_Type, ...] = (), force_subscriber_type_safety: bool = False):
		"""
		Constructs a new RefEvent.
		:param param_types: The param types of the event. When calling the event, these types must be obeyed, in order.
		:param force_subscriber_type_safety: Whether to verify the param types of the subscriber. An exception will be
		raised if the param types are mismatched.
		"""
		super().__init__()
		self._param_types = param_types
		self._force_subscriber_type_safety = force_subscriber_type_safety

	def __call__(self, *args) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		if len(args) != len(self._param_types):
			raise EventCallParameterListMismatchError
		for i, arg in enumerate(args):
			if not isinstance(arg, self._param_types[i]):
				raise EventCallParameterListMismatchError
		for subscriber in self._subs:
			if subscriber is not None:
				subscriber(*args)

	def _validate_subscriber(self, subscriber: _Callable):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		:raise: A BaseEventError, if the subscriber is invalid.
		"""
		if not isinstance(subscriber, _Callable):
			raise SubscriberIsNotCallableError
		subscriber_signature = _signature(subscriber)
		if len(subscriber_signature.parameters.values()) != len(self._param_types):
			raise SubscriberSignatureMismatchError
		if self._force_subscriber_type_safety:
			for i, param in enumerate(subscriber_signature.parameters.values()):
				if param.annotation != self._param_types[i] and param.annotation != param.empty:
					raise SubscriberSignatureMismatchError

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
