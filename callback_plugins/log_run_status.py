from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: log_run_status
    type: notification
    short_description: write run status to file
    version_added: historical
    description:
      - This callback writes run status out to file
    requirements:
     - None
'''

import os
import time
import json
from collections import MutableMapping

from ansible.module_utils._text import to_bytes
from ansible.plugins.callback import CallbackBase


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs run result to run_status.json and run_status (not JSON)
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'log_run_status'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.tasks_status = {}

    def log(self, host, category, data):
        if category not in self.tasks_status:
            self.tasks_status[category] = 1
        else:
            self.tasks_status[category] += 1;

    def runner_on_failed(self, host, res, ignore_errors=False):
        self.log(host, 'failed', res)

    def runner_on_ok(self, host, res):
        self.log(host, 'ok', res)
        if 'changed' in res and res['changed']:
            self.log(host, 'changed', res)

    def runner_on_skipped(self, host, item=None):
        self.log(host, 'skipped', res)

    def runner_on_unreachable(self, host, res):
        self.log(host, 'unreachable', res)
        self.log(host, 'failed', res)

    def runner_on_async_failed(self, host, res, jid):
        self.log(host, 'async_failed', res)
        self.log(host, 'failed', res)

    def playbook_on_import_for_host(self, host, imported_file):
        self.log(host, 'imported', res)

    def playbook_on_not_import_for_host(self, host, missing_file):
        self.log(host, 'not_imported', res)
        self.log(host, 'failed', res)

    def playbook_on_stats(self, stats):
        print("Playbook tasks status:")
        print(self.tasks_status)
        with open('run_status.json', 'w') as output_file:
            output_file.write(json.dumps(self.tasks_status))
        with open('run_status', 'w') as output_file:
            for key, value in self.tasks_status.iteritems():
                output_file.write("%s %s\n" % (key, value))
