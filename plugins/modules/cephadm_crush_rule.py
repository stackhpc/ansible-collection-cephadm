#!/usr/bin/python

# Copyright 2020, Red Hat, Inc.
# Copyright 2021, StackHPC, Ltd.
# NOTE: Files adapted from github.com/ceph/ceph-ansible
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: cephadm_crush_rule
short_description: Manage Ceph Crush Replicated/Erasure Rule
version_added: "1.4.0"
description:
    - Manage Ceph Crush rule(s) creation, deletion and updates.
author:
    - Dimitri Savineau <dsavinea@redhat.com>
    - Michal Nasiadka <michal@stackhpc.com>
options:
    name:
        description:
            - name of the Ceph Crush rule.
        required: true
        type: str
    state:
        description:
            If 'present' is used, the module creates a rule if it doesn't
            exist or update it if it already exists.
            If 'absent' is used, the module will simply delete the rule.
            If 'info' is used, the module will return all details about the
            existing rule (json formatted).
        required: false
        choices: ['present', 'absent', 'info']
        default: present
        type: str
    rule_type:
        description:
            - The ceph CRUSH rule type.
        required: false
        choices: ['replicated', 'erasure']
        type: str
    bucket_root:
        description:
            - The ceph bucket root for replicated rule.
        required: false
        type: str
    bucket_type:
        description:
            - The ceph bucket type for replicated rule.
        required: false
        choices: ['osd', 'host', 'chassis', 'rack', 'row', 'pdu', 'pod',
                 'room', 'datacenter', 'zone', 'region', 'root']
        type: str
    device_class:
        description:
            - The ceph device class for replicated rule.
        required: false
        type: str
    profile:
        description:
            - The ceph erasure profile for erasure rule.
        required: false
        type: str
'''

EXAMPLES = '''
- name: create a Ceph Crush replicated rule
  cephadm_crush_rule:
    name: foo
    bucket_root: default
    bucket_type: host
    device_class: ssd
    rule_type: replicated

- name: create a Ceph Crush erasure rule
  cephadm_crush_rule:
    name: foo
    profile: bar
    rule_type: erasure

- name: get a Ceph Crush rule information
  cephadm_crush_rule:
    name: foo
    state: info

- name: delete a Ceph Crush rule
  cephadm_crush_rule:
    name: foo
    state: absent
'''

RETURN = '''#  '''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stackhpc.cephadm.plugins.module_utils.cephadm_common \
    import generate_ceph_cmd, exec_command, exit_module

import datetime
import json


def create_rule(module, container_image=None):
    '''
    Create a new crush replicated/erasure rule
    '''

    name = module.params.get('name')
    rule_type = module.params.get('rule_type')
    bucket_root = module.params.get('bucket_root')
    bucket_type = module.params.get('bucket_type')
    device_class = module.params.get('device_class')
    profile = module.params.get('profile')

    if rule_type == 'replicated':
        args = ['create-replicated', name, bucket_root, bucket_type]
        if device_class:
            args.append(device_class)
    else:
        args = ['create-erasure', name]
        if profile:
            args.append(profile)

    cmd = generate_ceph_cmd(['osd', 'crush', 'rule'],
                            args)

    return cmd


def get_rule(module, container_image=None):
    '''
    Get existing crush rule
    '''

    name = module.params.get('name')

    args = ['dump', name, '--format=json']

    cmd = generate_ceph_cmd(['osd', 'crush', 'rule'],
                            args)

    return cmd


def remove_rule(module, container_image=None):
    '''
    Remove a crush rule
    '''

    name = module.params.get('name')

    args = ['rm', name]

    cmd = generate_ceph_cmd(['osd', 'crush', 'rule'],
                            args)

    return cmd


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', required=False, choices=['present', 'absent', 'info'], default='present'),  # noqa: E501
            rule_type=dict(type='str', required=False, choices=['replicated', 'erasure']),  # noqa: E501
            bucket_root=dict(type='str', required=False),
            bucket_type=dict(type='str', required=False, choices=['osd', 'host', 'chassis', 'rack', 'row', 'pdu', 'pod',  # noqa: E501
                                                                  'room', 'datacenter', 'zone', 'region', 'root']),  # noqa: E501
            device_class=dict(type='str', required=False),
            profile=dict(type='str', required=False)
        ),
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['rule_type']),
            ('rule_type', 'replicated', ['bucket_root', 'bucket_type']),
            ('rule_type', 'erasure', ['profile'])
        ]
    )

    # Gather module parameters in variables
    name = module.params.get('name')
    state = module.params.get('state')
    rule_type = module.params.get('rule_type')

    if module.check_mode:
        module.exit_json(
            changed=False,
            stdout='',
            stderr='',
            rc=0,
            start='',
            end='',
            delta='',
        )

    startd = datetime.datetime.now()
    changed = False

    if state == "present":
        rc, cmd, out, err = exec_command(module, get_rule(module))  # noqa: E501
        if rc != 0:
            rc, cmd, out, err = exec_command(module, create_rule(module))  # noqa: E501
            changed = True
        else:
            rule = json.loads(out)
            if (rule['type'] == 1 and rule_type == 'erasure') or (rule['type'] == 3 and rule_type == 'replicated'):  # noqa: E501
                module.fail_json(msg="Can not convert crush rule {0} to {1}".format(str(name), str(rule_type)), changed=False, rc=1)  # noqa: E501

    elif state == "absent":
        rc, cmd, out, err = exec_command(module, get_rule(module))  # noqa: E501
        if rc == 0:
            rc, cmd, out, err = exec_command(module, remove_rule(module))  # noqa: E501
            changed = True
        else:
            rc = 0
            out = "Crush Rule {0} doesn't exist".format(name)

    elif state == "info":
        rc, cmd, out, err = exec_command(module, get_rule(module))  # noqa: E501

    exit_module(module=module, out=out, rc=rc, cmd=cmd, err=err, startd=startd, changed=changed)  # noqa: E501


if __name__ == '__main__':
    main()
