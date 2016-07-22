#todo add documentation, tests and examples

class TimeBisectableArray(list):

    #start supported array operations
    def append(self, x):
        self._time_items_were_added.append(time.time())
        super(TimeBisectableArray, self).append(x)

    def pop(self, i=-1):
        self._time_items_were_added.pop(i)
        super(TimeBisectableArray, self).pop(i)

    def remove(self, x):
        del self._time_items_were_added[self._items.index(x)]
        super(TimeBisectableArray, self).remove(x)

    def extend(self, iterable):
        self._time_items_were_added.extend([time.time() for i in range(len(iterable))])
        super(TimeBisectableArray, self).extend(iterable)

    def __init__(self):
        self._items = []
        self._time_items_were_added = []
        super(TimeBisectableArray, self).__init__()

    def __delitem__(self, y):
        del self._time_items_were_added[y]
        del self._items[y]

    def __iadd__(self, y):
        """ x.__iadd__(y) <==> x+=y """
        self._time_items_were_added.__iadd__([time.time() for i in range(len(y))])
        return super(TimeBisectableArray, self).__iadd__(self, y)

    #End supported array operations

    #Start new Bisection operations

    def pop_lt(self, time_epoch_secs):
        """Pop elements entered before time_epoch_secs"""
        i = bisect.bisect(self._time_items_were_added, time_epoch_secs)
        if i:
            self._time_items_were_added = self._time_items_were_added[i:]
            popped = self._items[:i]
            self._items = self._items[i:]
            return popped
        raise ValueError

    def find_lt(self, time_epoch_secs):
        """Find rightmost value with insertion time less than time_epoch_secs"""
        i = bisect.bisect_left(self._time_items_were_added, time_epoch_secs)
        if i:
            return self._items[i-1]
        raise ValueError

    def find_le(self, time_epoch_secs):
        """Find rightmost value with insertion time less than or equal to time_epoch_secs"""
        i = bisect.bisect_right(self._time_items_were_added, time_epoch_secs)
        if i:
            return self._items[i-1]
        raise ValueError

    def find_gt(self, time_epoch_secs):
        """Find leftmost value with insertion time greater than time_epoch_secs"""
        i = bisect.bisect_right(self._time_items_were_added, time_epoch_secs)
        if i != len(self._items):
            return self._items[i]
        raise ValueError

    def find_ge(self, time_epoch_secs):
        """Find leftmost value with insertion time greater than or equal to time_epoch_secs"""
        i = bisect.bisect_left(self._time_items_were_added, time_epoch_secs)
        if i != len(self._items):
            return self._items[i]
        raise ValueError

    #End new Bisection operations

    #Start unsupported operations

    def sort(self, cmp=None, key=None, reverse=False):
        raise NotImplementedError('Data structure does not support this operation')

    def reverse(self):
        raise NotImplementedError('Data structure does not support this operation')

    def insert(self, i, x):
        raise NotImplementedError('Data structure does not support this operation')

    def __imul__(self, y):
        raise NotImplementedError('Data structure does not support this operation')
    #End unsupported operations

