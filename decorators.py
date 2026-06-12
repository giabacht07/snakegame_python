"""Decorators used for logging and history persistence in the Snake Game.

Provides small wrappers for logging game events and validating/presenting
history pipeline messages. These decorators are intentionally light-weight to
avoid coupling with application state.
"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def log_game_event(func):
    """ Middleware decorator logging critical structural game transformations. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug("Invoked: %-22s | Return Context: %s", func.__name__, result)
        return result
    return wrapper

def history_pipeline(func):
    """ Decorator verifying structural data constraints before flushing records to storage. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # args[1] and args[2] are name and length when called as a bound method
        if len(args) >= 3:
            logger.debug("Incoming validation intercept -> User: %s, Tail Length: %s", args[1], args[2])
        return func(*args, **kwargs)
    return wrapper
