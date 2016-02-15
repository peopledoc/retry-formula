import copy
import imp
import logging
import time


logger = logging.getLogger(__name__)


def get_state(module_name, function_name):
    mod = imp.load_module(
        module_name,
        *imp.find_module('salt/states/' + module_name))

    mod.__dict__['__salt__'] = __salt__  # noqa
    mod.__dict__['__env__'] = __env__  # noqa
    mod.__dict__['__opts__'] = __opts__  # noqa
    mod.__dict__['__grains__'] = __grains__  # noqa

    return getattr(mod, function_name)


class Retried(object):
    DEFAULT_SLEEP = 7
    DEFAULT_RETRIES = 20
    DEFAULT_MAX_SLEEP = 60

    def __init__(self, module_name, function_name, sleep=None, retries=None,
                 max_sleep=None):

        self.module_name = module_name
        self.function_name = function_name

        self.sleep = sleep if sleep else self.DEFAULT_SLEEP
        self.retries = retries if retries else self.DEFAULT_RETRIES
        self.max_sleep = max_sleep if max_sleep else self.DEFAULT_MAX_SLEEP

    def get_function(self):
        logger.debug(
            'Hijacking state %s.%s', self.module_name, self.function_name)

        def retrier(*args, **kwargs):
            result = dict()
            i = 0
            while result.get('result', False) is False:
                result = self.get_result(i, result, *args, **kwargs)

                if result['result'] is True or i > self.retries:
                    return result

                logger.debug("Retrying %r", result)

                i += 1
                time.sleep(
                    self.sleep * i
                    if self.sleep * i < self.max_sleep
                    else self.max_sleep)

            return result
        retrier.__name__ = self.function_name
        return retrier

    def get_result(self, tries, last_result, *args, **kwargs):
        return get_state(self.module_name, self.function_name)(
            *args, **kwargs)


class PkgRetried(Retried):
    def get_result(self, tries, last_result, *args, **kwargs):
        logger = logging.getLogger(__file__)

        if tries > 1:
            kwargs = copy.copy(kwargs)
            kwargs['refresh'] = True

        if tries > 2:
            result = __salt__['cmd.run']('apt-get -f install')  # noqa
            logger.debug(result)

        return get_state(self.module_name, self.function_name)(
            *args, **kwargs)


installed = PkgRetried('pkg', 'installed').get_function()
latest = PkgRetried('pkg', 'latest').get_function()
