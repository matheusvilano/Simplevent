import inspect
from typing import Callable
from abc import ABC, abstractmethod
from collections import OrderedDict


class Event(ABC):

	@abstractmethod
	def __init__(self, *, allow_duplicate_subscribers: bool = True):
		"""
		Constructs a new Event.
		:param allow_duplicate_subscribers: Whether to allow duplicate subscribers.
		"""
		self._subs: list = []
		self._allow_duplicate_subs = allow_duplicate_subscribers

	@abstractmethod
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
		self._validate_subscriber(subscriber)
		self.remove(subscriber)
		return self

	def __len__(self):
		"""
		Sugar syntax for checking the current amount of subscribers.
		:return: The current amount of subscribers.
		"""
		return len(self._subs)

	@abstractmethod
	def _validate_subscriber(self, subscriber):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		:raise: A BaseEventError, if the subscriber is invalid.
		"""
		pass

	def invoke(self, *args, **kwargs) -> None | list:
		"""
		Invokes the event, causing all subscribers to handle (respond to) the event.
		:param args: Named arguments.
		:param kwargs: Unnamed arguments.
		:return: No return value, by default.
		"""
		return self.__call__(*args, **kwargs)

	def add(self, subscriber):
		"""
		Adds a new subscriber.
		:param subscriber: The new subscriber.
		"""
		self._validate_subscriber(subscriber)
		if not self._allow_duplicate_subs and subscriber in self._subs:
			return
		self._subs.append(subscriber)

	def insert(self, i: int, subscriber):
		"""
		Inserts a new subscriber (at the specified index).
		:param i: The index where to insert the new subscriber.
		:param subscriber: The new subscriber
		"""
		self._validate_subscriber(subscriber)
		if not self._allow_duplicate_subs and subscriber in self._subs:
			return
		self._subs.insert(i, subscriber)

	def remove(self, subscriber):
		"""
		Removes a subscriber.
		:param subscriber: The subscriber to remove.
		"""
		self._subs.remove(subscriber)

	def remove_duplicate_subscribers(self):
		"""Removes duplicate subscribers from the Event. This method should be avoided, as the time it takes to run scales with the amount of subscribers."""
		self._subs = list(OrderedDict.fromkeys(self._subs))


class SignedEvent(Event):
	"""An event with functions (or functors) as subscribers. The expectation is that the subscribed (signed) function will always be called successfully."""

	def __init__(self, *, amount_of_params: int = None, return_from_subscribers: bool = False, allow_duplicate_subscribers: bool = False):
		"""
		Constructs a new SignedEvent.
		:param return_from_subscribers: Whether to forward return values from subscribers.
		:param allow_duplicate_subscribers: Whether to allow duplicate subscribers.
		"""
		super().__init__(allow_duplicate_subscribers=allow_duplicate_subscribers)
		self._len_params: int | None = amount_of_params
		self._return_from_subs: bool = return_from_subscribers

	def __call__(self, *args, **kwargs) -> None | list:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		if self._len_params is not None and self._len_params != len(args):
			raise IncorrectNumberOfArgsError
		return_values: list = []
		for subscriber in self._subs:
			if subscriber is not None:
				return_values.append(subscriber(*args, **kwargs))
		return return_values if self._return_from_subs else None

	def _validate_subscriber(self, subscriber):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		:raise: A BaseEventError, if the subscriber is invalid.
		"""
		subscriber_signature = inspect.signature(subscriber)
		if self._len_params is not None and self._len_params != len(subscriber_signature.parameters):
			raise IncorrectNumberOfParamsError
		if not isinstance(subscriber, Callable):
			raise NotCallableError


class NamedEvent(Event):
	"""An event with non-function objects as subscribers, that stores its name as a string. Once invoked, a NamedEvent will query its subscribers for a method of the same name as itself; if valid, the method is immediately called."""

	def __init__(self, event_name: str, *, allow_duplicate_subscribers: bool = False):
		"""
		Constructs a new SignedEvent.
		:param event_name: The name of the event. This is also the name of the callback function to look for in the event's subscribers.
		:param allow_duplicate_subscribers: Whether to allow duplicate subscribers.
		"""
		super().__init__(allow_duplicate_subscribers=allow_duplicate_subscribers)
		if not isinstance(event_name, str):
			raise InvalidEventNameError
		self._name = event_name

	def __call__(self, *args, **kwargs) -> None:
		"""
		Calls every single current subscriber, if valid.
		:param args: Unnamed arguments.
		:param kwargs: Named arguments.
		:return: No return value, by default.
		"""
		for subscriber in self._subs:
			if subscriber is not None:
				function = getattr(subscriber, self._name)
				if function is not None:
					function(*args, **kwargs)

	def _validate_subscriber(self, subscriber):
		"""
		Validates whether the subscriber is valid.
		:param subscriber: The subscriber to evaluate.
		"""
		pass  # At the moment, any subscriber is valid for NamedEvent objects.

	@property
	def name(self) -> str:
		"""
		The name of this event.
		:return:The name of this event.
		"""
		return self._name


class BaseEventError(BaseException):
	...


class EventSubscriptionError(BaseEventError):
	...


class InvalidEventNameError(BaseEventError):
	...


class EventInvocationError(BaseEventError):
	...


class IncorrectNumberOfArgsError(EventInvocationError):
	...


class IncorrectNumberOfParamsError(EventSubscriptionError):
	...


class WrongCallableSignatureError(EventSubscriptionError):
	...


class NotCallableError(EventSubscriptionError):
	...
