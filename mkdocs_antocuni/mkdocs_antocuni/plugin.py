"""Custom Plugin for antocuni.eu."""

import logging
import warnings
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class MyPlugin(BasePlugin):

    config_scheme = (
        ('silent', config_options.Type(bool, default=True)),
    )

    def on_startup(self, command, dirty):
        """Suppress redirects warnings."""

        print('hello from mkdocs_antocuni')

        # Create a custom filter to suppress redirects warnings
        class RedirectsFilter(logging.Filter):
            def filter(self, record):
                return not (record.levelno == logging.WARNING and
                           'redirects plugin:' in record.getMessage())

        # Add the filter to all existing loggers and the root logger
        for name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(name)
            logger.addFilter(RedirectsFilter())

        # Also add to root logger
        logging.getLogger().addFilter(RedirectsFilter())
