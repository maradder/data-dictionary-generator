"""
Timeout utilities for long-running operations.

Provides cross-platform timeout mechanisms for preventing infinite hangs.
Uses signal.alarm() on Unix/Linux systems (production containers).
"""

import logging
import signal
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TimeoutError(Exception):
    """Raised when an operation exceeds its timeout limit."""
    pass


def with_timeout(seconds: int | None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to add timeout protection to a function using signal.alarm().

    This implementation uses signal.SIGALRM which only works on Unix-like systems
    (Linux, macOS). Windows is not supported, but since production runs in Linux
    containers, this is acceptable.

    For Windows development without Docker, timeouts will be logged but not enforced.

    Args:
        seconds: Maximum time allowed for function execution (None to disable timeout)

    Returns:
        Decorated function with timeout protection

    Raises:
        TimeoutError: If function execution exceeds timeout

    Example:
        @with_timeout(30)
        def parse_large_xml(file_path):
            return etree.parse(file_path)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # If no timeout specified, just run the function
            if seconds is None:
                return func(*args, **kwargs)

            # Check if signal.alarm is available (Unix/Linux only)
            if not hasattr(signal, 'SIGALRM'):
                logger.warning(
                    f"Timeout protection not available on this platform. "
                    f"Function {func.__name__} will run without timeout. "
                    f"For production-like behavior, use Docker."
                )
                return func(*args, **kwargs)

            def timeout_handler(signum: int, frame: Any) -> None:
                raise TimeoutError(
                    f"Operation '{func.__name__}' timed out after {seconds} seconds"
                )

            # Set up the timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel the alarm
                return result
            except TimeoutError:
                signal.alarm(0)  # Cancel the alarm before re-raising
                logger.error(
                    f"Timeout in {func.__name__} after {seconds}s",
                    extra={'timeout_seconds': seconds, 'function': func.__name__}
                )
                raise
            finally:
                # Restore the original signal handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper
    return decorator


def timeout_context(seconds: int, operation_name: str = "operation"):
    """
    Context manager for timeout protection.

    Similar to with_timeout decorator but can be used as a context manager.

    Args:
        seconds: Maximum time allowed
        operation_name: Name of the operation for error messages

    Example:
        with timeout_context(30, "XML parsing"):
            result = etree.parse(file_path)
    """
    class TimeoutContext:
        def __enter__(self):
            if not hasattr(signal, 'SIGALRM'):
                logger.warning(
                    f"Timeout protection not available on this platform. "
                    f"{operation_name} will run without timeout."
                )
                self.enabled = False
                return self

            self.enabled = True

            def timeout_handler(signum: int, frame: Any) -> None:
                raise TimeoutError(
                    f"{operation_name} timed out after {seconds} seconds"
                )

            self.old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.enabled:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, self.old_handler)

            if isinstance(exc_val, TimeoutError):
                logger.error(
                    f"Timeout in {operation_name} after {seconds}s",
                    extra={'timeout_seconds': seconds, 'operation': operation_name}
                )
            return False  # Don't suppress exceptions

    return TimeoutContext()
