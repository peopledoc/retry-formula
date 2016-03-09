import copy
import logging

logger = logging.getLogger(__name__)


def _retried(module, function):
    def wrapper(*args, **kwargs):
        retried = __salt__['retried.get_module']()  # noqa

        class PkgRetried(retried.Retried):
            def get_result(self, tries, last_result, *args, **kwargs):
                logger = logging.getLogger(__file__)

                if tries > 1:
                    kwargs = copy.copy(kwargs)
                    kwargs['refresh'] = True

                if tries > 2:
                    result = __salt__['cmd.run']('apt-get -f install')  # noqa
                    logger.debug(result)

                return (
                    retried.get_state(
                        self.module_name, self.function_name, __env__  # noqa
                    )
                    (*args, **kwargs)
                )

        return (
            PkgRetried(module, function, __env__)  # noqa
            .get_function()(*args, **kwargs)
        )

    wrapper.__name__ = function
    return wrapper


installed = _retried('pkg', 'installed')
latest = _retried('pkg', 'latest')
