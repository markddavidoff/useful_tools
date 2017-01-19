from functools import wraps
import logging
from unittest import TestCase

logger = logging.getLogger(__name__)

class ThreadMemo(object):
    """
    A decorator to cache calls to this function on this thread. Individual
    threads have independent caches.

    To enable threading for a Thread for all ThreadMemo decorators,
    call ThreadMemo.enable_thread_memo_for_this_thread() BEFORE this decorator
    is called.

    WARNING 1: Requires call with empty args like so: @ThreadMemo()
        (note the parenthesis at the end)
    WARNING 2: Args must be hashable
    WARNING 3: prints all args and returns of a function. Setup decorator with
        @ThreadMemo(silence_logging=True) if you want to silence logging.
    """

    thread_local = local()

    def __init__(self, silence_logging=False):
        self.silence_logging = silence_logging

    def __call__(self, func):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """

        try:
            func_name = func.__name__
        except:
            func_name = str(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            memoize = ThreadMemo.is_memoize_enabled_for_this_thread()
            if memoize:
                try:
                    hashable_kwargs = tuple(kwargs[k] for k in sorted(kwargs.keys()))
                    hashed_args = hash((args, hashable_kwargs))
                    memo_map = ThreadMemo.get_memo_map_for_this_thread()
                    memo_result = memo_map.get(hashed_args)
                    if memo_result:
                        if not self.silence_logging:
                            logger.debug('Returning cached value {} for memoized call on func {} with args {}'.format(memo_result, func_name,  (args, kwargs)))
                        return memo_result
                except:
                    if not self.silence_logging:
                        logger.debug('Could not hash args {}, skipping thread memoization for func {}'.format((args, kwargs), func_name))
                    memoize = False

            result = func(*args, **kwargs)
            if memoize:
                try:
                    memo_map[hashed_args] = result
                except:
                    if not self.silence_logging:
                        logger.debug('Error saving result {} for memoizing, for func {} with args {}'.format(result, func_name, (args, kwargs)))

            return result

        return wrapper

    @staticmethod
    def enable_thread_memo_for_this_thread():
        ThreadMemo.thread_local.memoize_with_thread_memo = True

    @staticmethod
    def disable_thread_memo_for_this_thread():
        ThreadMemo.thread_local.memoize_with_thread_memo = False

    @staticmethod
    def is_memoize_enabled_for_this_thread():
        if not hasattr(ThreadMemo.thread_local, 'memoize_with_thread_memo'):
            ThreadMemo.thread_local.memoize_with_thread_memo = False
        return ThreadMemo.thread_local.memoize_with_thread_memo

    @staticmethod
    def get_memo_map_for_this_thread():
        if not hasattr(ThreadMemo.thread_local, 'memo_map'):
            ThreadMemo.thread_local.memo_map = {}
        return ThreadMemo.thread_local.memo_map


class ThreadMemoTests(TestCase):

    def setUp(self):
        global _memo_test_thread_local
        _memo_test_thread_local = threading.local()
        global run_count
        run_count = 0

        @ThreadMemo()
        def wrap_me(arg1, arg2, kwarg1=False, kwarg2='123'):
            global _memo_test_thread_local
            if hasattr(_memo_test_thread_local, '_thread_memo_test_run_count'):
                _memo_test_thread_local._thread_memo_test_run_count += 1
            else:
                _memo_test_thread_local._thread_memo_test_run_count = 1
            return arg1 + arg2

        self.wrap_me_func = wrap_me

    def test_basic_wrap(self):
        global run_count
        run_count = 0
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())
        # Thread memo is off:
        def _run_5_times_with_memo_off():

            for i in range(0, 5):
                self.wrap_me_func(1, 2, True)

            global run_count

            run_count = _memo_test_thread_local._thread_memo_test_run_count

        t1 = threading.Thread(target=_run_5_times_with_memo_off)
        t1.start()
        t1.join()
        self.assertEqual(5, run_count)
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())

        run_count = 0

        def _run_5_times_with_memo_on():
            ThreadMemo.enable_thread_memo_for_this_thread()
            for i in range(0, 5):
                self.wrap_me_func(1, 2, True)

            global run_count

            run_count = _memo_test_thread_local._thread_memo_test_run_count

        t1 = threading.Thread(target=_run_5_times_with_memo_on)
        t1.start()
        t1.join()
        self.assertEqual(1, run_count)
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())

    def test_enabled_then_disabled(self):
        global run_count
        run_count = 0

        def _run_3_times_with_memo_on_and_2_off():
            ThreadMemo.enable_thread_memo_for_this_thread()
            self.wrap_me_func(1, 2, True)
            self.wrap_me_func(1, 2, True)
            ThreadMemo.disable_thread_memo_for_this_thread()
            self.wrap_me_func(1, 2, True)
            self.wrap_me_func(1, 2, True)
            ThreadMemo.enable_thread_memo_for_this_thread()
            self.wrap_me_func(1, 2, True)

            global run_count

            run_count = _memo_test_thread_local._thread_memo_test_run_count

        t1 = threading.Thread(target=_run_3_times_with_memo_on_and_2_off)
        t1.start()
        t1.join()
        # will be 3 as the first run is counted as well
        self.assertEqual(3, run_count)
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())

    def switch_around_kwargs_order(self):
        global run_count
        run_count = 0
        def _run_5_times_with_memo_on():
            ThreadMemo.enable_thread_memo_for_this_thread()
            self.wrap_me_func(1, 2, kwarg2='456', kwarg1=True)
            for i in range(0, 4):
                self.wrap_me_func(1, 2, kwarg1=True, kwarg2='456')

            global run_count

            run_count = _memo_test_thread_local._thread_memo_test_run_count

        t1 = threading.Thread(target=_run_5_times_with_memo_on)
        t1.start()
        t1.join()
        self.assertEqual(1, run_count)
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())

    def test_non_hashable_args(self):
        # should just skip the memo
        global run_count
        run_count = 0
        def _run_5_times_with_memo_on():
            ThreadMemo.enable_thread_memo_for_this_thread()
            for i in range(0, 5):
                self.wrap_me_func(1, 2, {'secrets': [1,2]})

            global run_count

            run_count = _memo_test_thread_local._thread_memo_test_run_count

        t1 = threading.Thread(target=_run_5_times_with_memo_on)
        t1.start()
        t1.join()
        self.assertEqual(5, run_count)
        self.assertFalse(ThreadMemo.is_memoize_enabled_for_this_thread())
