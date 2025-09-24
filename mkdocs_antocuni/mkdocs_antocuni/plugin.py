"""Custom Plugin for antocuni.eu."""

import logging
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class MyPlugin(BasePlugin):

    config_scheme = (
        ('silent', config_options.Type(bool, default=True)),
    )

    def on_startup(self, command, dirty):
        """Patch the redirects plugin logger to suppress warnings."""

        print('hello from mkdocs_antocuni')

        if self.config.get('silent', True):
            # Get the redirects plugin logger and set it to ERROR level
            # This will suppress WARNING messages about non-existent markdown files
            redirects_logger = logging.getLogger('mkdocs.plugins.redirects')
            redirects_logger.setLevel(logging.ERROR)

            # Also suppress warnings from the general redirects namespace
            redirect_logger = logging.getLogger('mkdocs-redirects')
            redirect_logger.setLevel(logging.ERROR)
