# Simplevent

## Summary

Simplevent is a simple Event framework for Python, based on the Observer design pattern. The package is minimal: it 
defines the `Event` base class and the `SignedEvent` and `NamedEvent` subclasses. An instance of either encapsulates
a `list` but **will also itself behave somewhat like a `list`**; this is essentially an _indirection_.

## Observer Pattern

Simplevent's minimalist framework can be seen as a variation on the [Observer Pattern](https://en.wikipedia.org/wiki/Observer_pattern):

- When you instantiate an `Event`, that instance's context (scope) is the `subject`.
- When you subscribe an object to an `Event`, that object is an `observer`.
- When you `invoke` an `Event` instance, you're notifying all `observers` that the `subject` has executed an important 
action.

## Motivation

Simplevent was a creation inspired by C# and its event framework that's already built into the language. The lack of a 
similar system in Python can hinder event-driven designs. Designing a framework - even one as simple as Simplevent - 
can be time-consuming. This package provides an easy, small-scale solution for event-driven programming.

## Event Types

There are two types of `Event` in Simplevent: `StrEvent` and `RefEvent`. Both share a few similarities:

- Subscribers are encapsulated in a `list`, which is encapsulated by the `Event`.
- Subscribing the same object twice is not allowed. In other words, duplicates are not supported.
- Some sugar syntax is available: `+=` (subscribe), `-=` (unsubscribe), and `()` (invoke).
- Some magic method compatibility is available; e.g. `len`.

Each type can be customized/configured via their respective constructor. Refer to `docstrings` for more information.

### Str Event

An `StrEvent` is an `Event` that stores a "callback name" as a `string`. Once invoked, it will go through all of its 
`subscribers`, looking for a method name that matches the stored `string`. 

Here's an example where a video-game Character is supposed to stop moving after a Timer has reached zero, with 
simplified code:

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

For events that broadcast data (information about the event), `StrEvent` supports **named parameters**. Here is a small 
snippet:

```python
from simplevent import StrEvent
energy_restored = StrEvent("on_energy_restored", "amount_restored")
# some subscriptions would happen here ...
# the expected signature is func(amount_restored: float) for direct access or func(**kwargs) for dictionary access
energy_restored(25.4)  # The event will call on_energy_restored on all subscribers and pass 25.4 or {"amount_restored": 25.4}
```

### Ref Event

`Subscribers` of a `RefEvent` **must be `Callable` objects**. In other words, the `Subscriber` has to be a `function`, 
a `method`, or a "functor-like" `object` (an `object` with the`__call__`magic method overloaded). That's because a 
`RefEvent` - unlike an `StrEvent`- will call its `Subscribers` directly **instead** of looking for a `method` of a 
certain name.

Here's the same example as in `StrEvent` - a video-game Character that is supposed to stop moving after a Timer has 
reached zero - but using `RefEvent` instead, again with simplified code:

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

For events that broadcast data (information about the event), `RefEvent` supports type-safe **signed parameters**. Type 
safety is ensured via type hints, which are fetched at runtime via the `inspect` built-in module. Here is a small 
snippet:

```python
from simplevent import RefEvent
energy_restored = RefEvent(float)
# some subscriptions would happen here ...
energy_restored(25.4)  # The event will call all subscribers and pass 25.4 (the amount of energy restored) via *args.
```

When defining events using `RefEvents` with parameters, make sure to document them, preferably with docstrings. This 
will ensure clarity and readability, specially with a long parameter list.

## Important Notes

### No Reference Management

Simplevent's `Event` instances do not automatically manage references to their `Subscribers`. That means it is up to the 
developer to manage references. Here are a couple of examples:

#### Null Subscribers
- `o` (an `object`) becomes a `Subscriber` of `e` (an `Event`).
- `o` is destroyed via `del` before being unsubscribed from `e`.

The above is a problem because `e` will still attempt to call `o` when invoked, which will result in an `Error` (likely 
a `TypeError`,`AttributeError`, or similar).

#### Persistent Subscribers
- `o` (an `object`) becomes a `Subscriber` of `e` (an `Event`).
- `o` is unreferenced everywhere in code, except in `e` (as a `subscriber`).

`o` exists inside `e` as a reference. Python's garbage collection will **not destroy `o`** until all references to it  
cease to exist - **including the one inside `e`, which represents `o` as a `Subscriber`**. The developer must be very 
careful and ensure that `o` is unsubscribed from `e` whenever needed.
