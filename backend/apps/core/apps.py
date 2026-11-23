import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        # Compatibility fix for Python 3.14+ where copy(super()) inside
        # BaseContext.__copy__ returns a super proxy rather than copying the context.
        if sys.version_info >= (3, 14):
            from django.template.context import BaseContext

            def _base_context_copy(self):
                duplicate = self.__class__.__new__(self.__class__)
                duplicate.__dict__.update(self.__dict__)
                duplicate.dicts = self.dicts[:]
                return duplicate

            BaseContext.__copy__ = _base_context_copy
