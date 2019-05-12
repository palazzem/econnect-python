from .exceptions import PermissionDenied, LockNotAcquired


def require_session(func):
    """Decorator applied to functions that require a valid Session.
    The session ID is verified in the instance for the attribute
    `_session_id`.

    Raises:
        InvalidSession: if a `session_id` is not available or expired.
    """

    def func_wrapper(*args, **kwargs):
        self = args[0]
        if self._session_id is None:
            raise PermissionDenied("You do not have permission to perform this action.")
        else:
            return func(*args, **kwargs)

    return func_wrapper


def require_lock(func):
    """Decorator applied to functions that require to obtain a system lock.
    The lock is verified in the instance for the attribute `_lock` that must
    be a `threading.Lock` class.

    Raises:
        LockNotAcquired: if a Lock is not acquired.
    """

    def func_wrapper(*args, **kwargs):
        self = args[0]
        # If the Lock() acquisition succeed it means a locking is not occurring
        # and so bail-out the execution (and release the lock).
        if self._lock.acquire(False):
            self._lock.release()
            raise LockNotAcquired("A lock must be acquired via `lock()` method.")
        else:
            return func(*args, **kwargs)

    return func_wrapper
