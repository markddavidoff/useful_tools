# todo add docs and tests

class memoize:

    class MetaData:
        def __init__(self, kwargs):
            self.kwargs =kwargs
            self.created = time.time()

    def __init__(self, list_of_kwargs_to_memoize, cache_lifetime_secs=60*60*24, garbage_collection_interval_secs=60*60):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.kwargs_to_memoize = list_of_kwargs_to_memoize
        self.cache_lifetime_secs = cache_lifetime_secs
        self.key_to_metadata = {}
        self.garbage_man= PeriodicWorker(self._garbage_collect,
                                              garbage_collection_interval_secs,
                                              daemon=True)
        self.garbage_man.start()

    def _garbage_collect(self):
        expiry_cutoff = time.time() - self.cache_lifetime_secs

        for key, metadata in self.key_to_metadata.iteritems():
            if metadata.created < expiry_cutoff:
                if key in self.memodict:
                    del self.memodict[key]
                del self.key_to_metadata[key]

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        kwargs_to_memoize = self.kwargs_to_memoize
        key_to_metadata = self.key_to_metadata
        class memodict(dict):
            def __getitem__(self, *args, **kwargs):
                if len(args) > 0:
                    raise Exception('Code Error: @memoize decorated functions must be called with kwargs, not args')

                # key is based on a subset of the args
                key = self.get_key_subset(kwargs)
                # store the time and kwargs
                key_to_metadata[key] = memoize.MetaData(kwargs)

                return dict.__getitem__(self, key)

            def __missing__(self, key):
                # if no cached result, evaluate and save the result
                ret = self[key] = f(**key_to_metadata[key].kwargs)

                return ret

            def get_key_subset(self, kwargs):
                return tuple(kwargs[k] for k in kwargs_to_memoize if k in kwargs)

        self.memodict = memodict()
        return self.memodict.__getitem__
