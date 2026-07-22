#!/usr/bin/python

# Copyright 2018, Red Hat, Inc.
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
module: cephadm_key

author: Sebastien Han <seb@redhat.com>
        Michal Nasiadka <michal@stackhpc.com>
version_added: "1.4.0"
short_description: Manage Cephx key(s)

description:
    - Manage CephX creation, deletion and updates.
      It can also list and get information about keyring(s).

options:
    name:
        description:
            - name of the CephX key
        required: false
        type: str
    state:
        description:
            - If 'present' is used, the module ensures a keyring exists
              with the associated capabilities.
              If 'absent' is used, the module will simply delete the keyring.
              If 'list' is used, the module will list all the keys and will
              return a json output.
              If 'info' is used, the module will return in a json format the
              description of a given keyring.
        required: false
        choices: ['present', 'absent', 'list', 'info']
        default: present
        type: str
    caps:
        description:
            - CephX key capabilities
        default: {}
        required: false
        type: dict
    key:
        description:
            - Secret value of the key. If specified, this key will be
              used explicitly instead of being generated.
        required: false
        type: str
    output_format:
        description:
            - The key output format when retrieving the information of an
              entity.
        required: false
        choices: ['json', 'plain', 'xml', 'yaml']
        default: json
        type: str
'''

EXAMPLES = '''
- name: create cephx key
  cephadm_key:
    name: "{{ item.name }}"
    state: present
    caps: "{{ item.caps }}"
  with_items: "{{ keys_to_create }}"

- name: delete cephx key
  cephadm_key:
    name: "my_key"
    state: absent

- name: info cephx key
  cephadm_key:
    name: "my_key"
    state: info

- name: info cephx admin key (plain)
  cephadm_key:
    name: client.admin
    output_format: plain
    state: info
  register: client_admin_key

- name: list cephx keys
  cephadm_key:
    state: list
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stackhpc.cephadm.plugins.module_utils.cephadm_common \
    import fatal, generate_ceph_cmd
import datetime
import json


def str_to_bool(val):
    try:
        val = val.lower()
    except AttributeError:
        val = str(val).lower()
    if val == 'true':
        return True
    elif val == 'false':
        return False
    else:
        raise ValueError("Invalid input value: %s" % val)


def generate_caps(caps):
    '''
    Generate CephX capabilities list
    '''

    caps_cli = []

    for k, v in caps.items():
        caps_cli.extend([k, v])

    return caps_cli


def create_key(name, caps):  # noqa: E501
    '''
    Create a CephX key
    '''
    cmd = []

    args = [
        'get-or-create',
        name
    ]

    args.extend(generate_caps(caps))
    cmd.append(generate_ceph_cmd(sub_cmd=['auth'],
                                 args=args))

    return cmd


def create_key_by_import(name, caps, key):
    '''
    Create a CephX key by import
    '''
    cmd = []

    caps_cli = []
    for k, v in caps.items():
        caps_cli.append(f'caps {k} = "{v}"')

    key_entry = f"[{name}]\n\tkey = {key}\n\t" + "\n\t".join(caps_cli)

    sub_cmd = ['auth', 'import']
    args = ['-i', '-']
    cmd.append(generate_ceph_cmd(sub_cmd=sub_cmd, args=args, key_entry=key_entry))

    return cmd


def update_key(name, caps):
    '''
    Update the caps of a CephX key
    '''

    cmd = []

    args = [
        'caps',
        name,
    ]
    args.extend(generate_caps(caps))
    cmd.append(generate_ceph_cmd(sub_cmd=['auth'],
                                 args=args))

    return cmd


def update_key_by_import(name, caps, key=None):
    '''
    Update a CephX key by re-importing it
    '''
    cmd = create_key_by_import(name, caps, key)

    return cmd


def delete_key(name):
    '''
    Delete a CephX key
    '''

    cmd = []

    args = [
        'del',
        name,
    ]

    cmd.append(generate_ceph_cmd(sub_cmd=['auth'],
                                 args=args))

    return cmd


def get_key(name, dest):
    '''
    Get a CephX key (write on the filesystem)
    '''

    cmd = []

    args = [
        'get',
        name,
        '-o',
        dest,
    ]

    cmd.append(generate_ceph_cmd(sub_cmd=['auth'],
                                 args=args))

    return cmd


def info_key(name, output_format):
    '''
    Get information about a CephX key
    '''

    cmd_list = []

    args = [
        'get',
        name,
        '-f',
        output_format,
    ]

    cmd_list.append(generate_ceph_cmd(sub_cmd=['auth'],
                                      args=args))

    return cmd_list


def list_keys():
    '''
    List all CephX keys
    '''

    cmd = []

    args = [
        'ls',
        '-f',
        'json',
    ]

    cmd.append(generate_ceph_cmd(sub_cmd=['auth'],
                                 args=args))

    return cmd


def exec_commands(module, cmd_list):
    '''
    Execute command(s)
    '''

    for cmd in cmd_list:
        rc, out, err = module.run_command(cmd)
        if rc != 0:
            return rc, cmd, out, err

    return rc, cmd, out, err


def run_module():
    module_args = dict(
        name=dict(type='str', required=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent',  # noqa: E501
                                                                           'list', 'info']),  # noqa: E501
        caps=dict(type='dict', required=False, default={}),
        key=dict(type='str', required=False, default=None),
        output_format=dict(type='str', required=False, default='json', choices=['json', 'plain', 'xml', 'yaml'])  # noqa: E501
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Gather module parameters in variables
    state = module.params['state']
    name = module.params.get('name')
    caps = module.params.get('caps')
    key = module.params.get('key')
    output_format = module.params.get('output_format')

    changed = False

    result = dict(
        changed=changed,
        stdout='',
        stderr='',
        rc=0,
        start='',
        end='',
        delta='',
    )

    if module.check_mode:
        module.exit_json(**result)

    startd = datetime.datetime.now()

    # Test if the key exists, if it does we skip its creation
    # We only want to run this check when a key needs to be added
    # There is no guarantee that any cluster is running and we don't need one
    _caps = caps
    key_exist = 1

    if state == "present":
        _info_key = []
        rc, cmd, out, err = exec_commands(
            module, info_key(name, output_format))  # noqa: E501
        key_exist = rc
        if not caps and key_exist != 0:
            fatal("Capabilities must be provided when state is 'present'", module)  # noqa: E501
        if key_exist == 0:
            _info_key = json.loads(out)
            if not caps:
                caps = _info_key[0]['caps']
            _caps = _info_key[0]['caps']
            if caps == _caps:
                result["stdout"] = "{0} already exists and doesn't need to be updated.".format(name)  # noqa: E501
                result["rc"] = 0
                module.exit_json(**result)
            else:
                if key and key != _key:
                    rc, cmd, out, err = exec_commands(
                        module, update_key_by_import(name, caps, key))  # noqa: E501
                else:
                    rc, cmd, out, err = exec_commands(
                        module, update_key(name, caps))  # noqa: E501
                if rc != 0:
                    result["stdout"] = "Couldn't update {0}".format(name)
                    result["stderr"] = err
                    module.exit_json(**result)
                changed = True

        else:
            if key:
                rc, cmd, out, err = exec_commands(module, create_key_by_import(name, caps, key))
                if rc != 0:
                    result["stdout"] = "Couldn't import {0}".format(name)
                    result["stderr"] = err
                    module.exit_json(**result)
                changed = True
            else:
                rc, cmd, out, err = exec_commands(module, create_key(name, caps))  # noqa: E501
                if rc != 0:
                    result["stdout"] = "Couldn't create {0}".format(name)
                    result["stderr"] = err
                    module.exit_json(**result)
                changed = True

    elif state == "absent":
        rc, cmd, out, err = exec_commands(
            module, info_key(name, output_format))  # noqa: E501
        key_exist = rc
        if key_exist == 0:
            rc, cmd, out, err = exec_commands(
                module, delete_key(name))  # noqa: E501
            if rc == 0:
                changed = True
        else:
            rc = 0

    elif state == "info":
        rc, cmd, out, err = exec_commands(
            module, info_key(name, output_format))  # noqa: E501

    elif state == "list":
        rc, cmd, out, err = exec_commands(
            module, list_keys())

    endd = datetime.datetime.now()
    delta = endd - startd

    result = dict(
        cmd=cmd,
        start=str(startd),
        end=str(endd),
        delta=str(delta),
        rc=rc,
        stdout=out.rstrip("\r\n"),
        stderr=err.rstrip("\r\n"),
        name=name,
        changed=changed,
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
