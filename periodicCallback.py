import tornado.ioloop


class PeriodicCallback(object):
    """
    用法: PeriodicCallback(函数名,间隔秒数,#ip_loop).start(函数参数)

    """

    def __init__(self, callback, callback_time, io_loop=None):
        self.callback = callback
        if callback_time <= 0:
            raise ValueError("Periodic callback must have a positive callback_time")
        self.callback_time = callback_time
        self.io_loop = io_loop or tornado.ioloop.IOLoop.current()
        self._running = False
        self._timeout = None

    def start(self, *args, **kwargs):
        """Starts the timer."""
        self._running = True
        self._next_timeout = self.io_loop.time()
        self._schedule_next(*args, **kwargs)

    def stop(self):
        """Stops the timer."""
        self._running = False
        if self._timeout is not None:
            self.io_loop.remove_timeout(self._timeout)
            self._timeout = None

    def _run(self, *args, **kwargs):
        if not self._running:
            return
        try:
            return self.callback(*args, **kwargs)
        except Exception:
            self.io_loop.handle_callback_exception(self.callback)
        finally:
            self._schedule_next(*args, **kwargs)

    def _schedule_next(self, *args, **kwargs):
        if self._running:
            current_time = self.io_loop.time()
            while self._next_timeout <= current_time:
                self._next_timeout += self.callback_time
            self._timeout = self.io_loop.add_timeout(self._next_timeout, self._run, *args, **kwargs)