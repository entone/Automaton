def level(level=0, redirect_template="invalid_permissions.html"):
    def wrap(func):
        def doit(obj, *args, **kwargs):
            if not hasattr(obj.session, 'user_obj') or not obj.session.user_obj.allowed(level):
                return obj.default_response(redirect_template)
            
            return func(obj, *args, **kwargs)

        doit.__name__ = func.__name__
        return doit
    return wrap
            