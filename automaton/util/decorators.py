def level(level=0):
    def wrap(func):
        def doit(obj, *args, **kwargs):
            if not hasattr(obj.session, 'user_obj') or not obj.session.user_obj.allowed(level):
                raise Exception("You do not have permissions to execute this action")

            return func(obj, *args, **kwargs)

        doit.__name__ = func.__name__
        return doit
    return wrap
            