# Simplevent

## Summary

Simplevent is a simple Event framework for Python, loosely based on the Observer design pattern. The package is minimal:
it defines the `Event` base class and the `SignedEvent` and `NamedEvent` subclasses. An instance of either encapsulates
a `list` but **will also itself behave somewhat like a `list`**; this is essentially an _indirection_.

## Observer Pattern

Simplevent's tiny framework can be seen as a variation on the [Observer Pattern](https://en.wikipedia.org/wiki/Observer_pattern):

- When you instantiate an `Event`, that instance's context (scope) is the `subject`.
- When you subscribe an object to an `Event`, that object is an `observer`.
- When you `invoke` an `Event` instance, you're notifying all `observers` that the `subject` has executed an important action.

## Motivation

Simplevent was a creation inspired by C# and its event framework that's already built into the language. The lack of a 
similar system in Python can hinder event-driven designs. Designing a framework - even one as simple as Simplevent - 
can be time-consuming. This package provides an easy, small-scale solution for event-driven programming.

## Event Types

There are two types of `Event` in Simplevent: `StrEvent` and `RefEvent`. Both share a few similarities:

- Subscribers are encapsulated in a `list`, which is encapsulated by the `Event`.
- Subscribing the same object twice is not allowed by default (but this can be changed).
- Some sugar syntax is available: `+=` (subscribe), `-=` (unsubscribe), and `()` (invoke).
- Some magic method compatibility is available: `len` (currently the only one).

Each type can be customized/configured via their respective constructor. Refer to `docstrings` for more information.

### Str Event

An `StrEvent` is an `Event` that stores a "callback name" as a `string`. Once invoked, it will go through all of its 
`subscribers`, looking for a method name that matches the stored `string`. 

Here's an example where a video-game Character 
is supposed to stop moving after a Timer has reached zero, with simplified code:

#### Example
```python
from simplevent import StrEvent

class Timer:
    
    def __init__(self, init_time: float = 60):
        """
        Initialized the timer.
        :param init_time: The initial time, in seconds.
        """
        self._time_left = init_time
        self.time_is_up = StrEvent("on_time_is_up")  # The event is defined here.
    
    def start_timer(self):
        """Starts the timer."""
        coroutine.start(self.decrease_time, loop_time=1, delay_time=0)
        
    def stop_timer(self):
        """Stops the timer."""
        coroutine.stop(self.decrease_time)
    
    def decrease_time(self):
        """Decreases the time by 1."""
        self._time_left -= 1
        if self._time_left <= 0:
            self.stop_timer()
            self.time_is_up()  # Sugar syntax; same as `self._time_is_up.invoke()`

class PlayerCharacter(ControllableGameObject):
    
    def __init__(self):
        self._is_input_enabled = True
        GameMode.get_global_timer().time_is_up += self  # Sugar syntax; same as `self._time_is_up.add(self)`
        # Other code ...
        # ...
        
    def enable_input(self):
        """Enabled user input (e.g. movement, etc)."""
        self._is_input_enabled = True

    def disable_input(self):
        """Disables user input (e.g. movement, etc)."""
        self._is_input_enabled = False
        
    def on_time_is_up(self):
        """Called automatically when the global timer has reached zero."""
        self.disable_input()

    # Other code ...
    # ...
```

### Ref Event

`Subscribers` of a `RefEvent` **must be `Callable` objects**. In other words, the `Subscriber` has to be a `function`, a `method`, 
or a "functor-like" `object` (an `object` with the`__call__`magic method overloaded). That's because a `RefEvent` - unlike 
an `StrEvent`- will call its `Subscribers` directly **instead** of looking for a `method` of a certain name.

Here's the same example as in `StrEvent` - a video-game Character that is supposed to stop moving after a Timer has reached 
zero - but using `RefEvent` instead, again with simplified code:

#### Example
```python
from simplevent import RefEvent

class Timer:
    
    def __init__(self, init_time: float = 60):
        """
        Initialized the timer.
        :param init_time: The initial time, in seconds.
        """
        self._time_left = init_time
        self.time_is_up = RefEvent()  # The event is defined here.
    
    def start_timer(self):
        """Starts the timer."""
        coroutine.start(self.decrease_time, loop_time=1, delay_time=0)
        
    def stop_timer(self):
        """Stops the timer."""
        coroutine.stop(self.decrease_time)
    
    def decrease_time(self):
        """Decreases the time by 1."""
        self._time_left -= 1
        if self._time_left <= 0:
            self.stop_timer()
            self.time_is_up()  # Sugar syntax; same as `self._time_is_up.invoke()`

class PlayerCharacter(ControllableGameObject):
    
    def __init__(self):
        self._is_input_enabled = True
        GameMode.get_global_timer().time_is_up += self.disable_input  # Sugar syntax; same as `self._time_is_up.add(self.disable_input)`
        # Other code ...
        # ...
        
    def enable_input(self):
        """Enabled user input (e.g. movement, etc)."""
        self._is_input_enabled = True

    def disable_input(self):
        """Disables user input (e.g. movement, etc)."""
        self._is_input_enabled = False

    # Other code ...
    # ...
```
