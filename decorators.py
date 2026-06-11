"""Decorators used for logging and history persistence in the Snake Game.

Provides small wrappers for logging game events and validating/presenting
history pipeline messages. These decorators are intentionally light-weight to
avoid coupling with application state.
"""

from functools import wraps


def log_game_event(func):
    """ Middleware decorator logging critical structural game transformations. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"[EVENT-STREAM] Invoked: {func.__name__:<22} | Return Context: {result}")
        return result
    return wrapper

def history_pipeline(func):
    """ Decorator verifying structural data constraints before flushing records to storage. """
    @wraps(func)
    def wrapper(manager_instance, name, length):
        # Simple auditing hook used during development and tests. In a
        # production setting consider using a proper logging framework.
        print(
            f"[DATA-PIPELINE] Incoming validation intercept -> User: {name}, "
            f"Tail Length: {length}"
        )
        return func(manager_instance, name, length)
    return wrapper
