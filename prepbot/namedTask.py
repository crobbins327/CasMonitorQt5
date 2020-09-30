import asyncio
import weakref
import itertools

_task_name_counter = itertools.count(1).__next__

def _set_task_name(task, name):
    if name is not None:
        try:
            set_name = task.set_name
        except AttributeError:
            print('AttributeError???')
            pass
        else:
            set_name(name)

class namedTask(asyncio.Task):

    # Weak set containing all tasks alive.
    _all_tasks = weakref.WeakSet()

    @classmethod
    def all_tasks(cls, loop=None):
        """Return a set of all tasks for an event loop.

        By default all tasks for the current event loop are returned.
        """
        if loop is None:
            loop = asyncio.get_event_loop()
        return {t for t in cls._all_tasks if t._loop is loop}

    def __init__(self, coro, *, loop=None, name=None):
        asyncio.Task.__init__(self, coro, loop=None)
        if name is None:
            self._name = f'Task-{_task_name_counter()}'
        else:
            self._name = str(name)
        self.__class__._all_tasks.add(self)

    def get_coro(self):
        return self._coro

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = str(value)

_PyTask = namedTask


def create_task(coro, *, name=None):
    """Schedule a coroutine object.
    Return a task object.
    """
    loop = asyncio.get_event_loop()
    loop._check_closed()
    if loop._task_factory is None:
        task = namedTask(coro, loop=loop, name=name)
        if task._source_traceback:
            del task._source_traceback[-1]
    else:
        task = loop._task_factory(coro)
        _set_task_name(task, name)

    return task



