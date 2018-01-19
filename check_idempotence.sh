#!/bin/bash
set -e

echo "First run:"
ansible-playbook ${@}

echo "Second run to check idempotence:"
ansible-playbook ${@}

grep "changed 0" run_status &>/dev/null || (echo -e "\nIdempotence failed!\n"; exit 1)
