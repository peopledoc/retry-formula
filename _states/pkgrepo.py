

def _retried(module, function):
    def wrapper(*args, **kwargs):
        retried = __salt__['retried.get_module']()  # noqa
        return (
            retried.Retried(module, function, __env__)
            .get_function()(*args, **kwargs)
            )

    wrapper.__name__ = function
    return wrapper


managed = _retried('pkgrepo', 'managed')
absent = _retried('pkgrepo', 'absent')
