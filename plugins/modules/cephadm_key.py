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
            - If 'present' is used, the module creates a keyring
              with the associated capabilities.
              If 'present' is used and a secret is provided the module
              will always add the key. Which means it will update
              the keyring if the secret changes, the same goes for
              the capabilities.
              If 'absent' is used, the module will simply delete the keyring.
              If 'list' is used, the module will list all the keys and will
              return a json output.
              If 'info' is used, the module will return in a json format the
              description of a given keyring.
              If 'generate_secret' is used, the module will simply output a
              cephx keyring.
        required: false
        choices: ['present', 'update', 'absent', 'list', 'info',
                  'fetch_initial_keys', 'generate_secret']
        default: present
        type: str
    caps:
        description:
            - CephX key capabilities
        default: {}
        required: false
        type: dict
    secret:
        description:
            - keyring's secret value
        required: false
        default: ''
        type: str
    dest:
        description:
            - destination directory to save key
        required: false
        default: "/etc/ceph/"
        type: str
    import_key:
        description:
            - Whether or not to import the created keyring into Ceph.
              This can be useful for someone that only wants to generate
              keyrings but not add them into Ceph.
        required: false
        default: True
        type: bool
    output_format:
        description:
            - The key output format when retrieving the information of an
              entity.
        required: false
        choices: ['json', 'plain', 'xml', 'yaml']
        default: json
        type: str
    attributes:
        aliases:
            - attr
        description:
            - File attributes
        required: false
        type: str
    group:
        description:
            - Group name for file ownership
        required: false
        type: str
    mode:
        description:
            - File permission mode
        required: false
        type: raw
    owner:
        description:
            - File owner
        required: false
        type: str
    selevel:
        description:
            - SELinux level
        required: false
        type: str
    serole:
        description:
            - SELinux role
        required: false
        type: str
    setype:
        description:
            - SELinux type
        required: false
        type: str
    seuser:
        description:
            - SELinux user
        required: false
        type: str
    unsafe_writes:
        description:
            - Enable unsafe writes
        required: false
        default: false
        type: bool
'''

EXAMPLES = '''
- name: create cephx key
  ceph_key:
    name: "{{ item.name }}"
    state: present
    caps: "{{ item.caps }}"
  with_items: "{{ keys_to_create }}"

- name: create cephx key but don't import it in Ceph
  ceph_key:
    name: "{{ item.name }}"
    state: present
    caps: "{{ item.caps }}"
    import_key: False
  with_items: "{{ keys_to_create }}"

- name: delete cephx key
  ceph_key:
    name: "my_key"
    state: absent

- name: info cephx key
  ceph_key:
    name: "my_key"
    state: info

- name: info cephx admin key (plain)
  ceph_key:
    name: client.admin
    output_format: plain
    state: info
  register: client_admin_key

- name: list cephx keys
  ceph_key:
    state: list
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stackhpc.cephadm.plugins.module_utils.cephadm_common \
    import fatal, generate_ceph_cmd
import datetime
import json
import os
import struct
import time
import base64


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


def generate_secret():
    '''
    Generate a CephX secret
    '''

    key = os.urandom(16)
    header = struct.pack('<hiih', 1, int(time.time()), 0, len(key))
    secret = base64.b64encode(header + key)

    return secret


def generate_caps(_type, caps):
    '''
    Generate CephX capabilities list
    '''

    caps_cli = []

    for k, v in caps.items():
        # makes sure someone didn't pass an empty var,
        # we don't want to add an empty cap
        if len(k) == 0:
            continue
        if _type == "ceph-authtool":
            caps_cli.extend(["--cap"])
        caps_cli.extend([k, v])

    return caps_cli


def generate_ceph_authtool_cmd(name, secret, caps, dest):  # noqa: E501
    '''
    Generate 'ceph-authtool' command line to execute
    '''

    cmd = [
        'cephadm',
        '--timeout',
        '30',
        'shell',
        '--',
        'ceph-authtool',
        '--create-keyring',
        dest,
        '--name',
        name,
        '--add-key',
        secret,
    ]

    cmd.extend(generate_caps("ceph-authtool", caps))

    return cmd


def create_key(module, result, name, secret, caps, import_key, dest):  # noqa: E501
    '''
    Create a CephX key
    '''

    cmd_list = []
    if not secret:
        secret = generate_secret()

    cmd_list.append(generate_ceph_authtool_cmd(
        name, secret, caps, dest))

    if import_key:
        args = ['get-or-create', name]
        args.extend(generate_caps(None, caps))
        args.extend(['-o', dest])
        cmd_list.append(generate_ceph_cmd(sub_cmd=['auth'],
                                          args=args))

    return cmd_list


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

    cmd_list = []

    args = [
        'get',
        name,
        '-o',
        dest,
    ]

    cmd_list.append(generate_ceph_cmd(sub_cmd=['auth'],
                                      args=args))

    return cmd_list


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

    cmd_list = []

    args = [
        'ls',
        '-f',
        'json',
    ]

    cmd_list.append(generate_ceph_cmd(sub_cmd=['auth'],
                                      args=args))

    return cmd_list


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
        state=dict(type='str', required=False, default='present', choices=['present', 'update', 'absent',  # noqa: E501
                                                                           'list', 'info', 'fetch_initial_keys', 'generate_secret']),  # noqa: E501
        caps=dict(type='dict', required=False, default={}),
        secret=dict(type='str', required=False, default='', no_log=True),
        import_key=dict(type='bool', required=False, default=True),
        dest=dict(type='str', required=False, default='/etc/ceph/'),
        output_format=dict(type='str', required=False, default='json', choices=['json', 'plain', 'xml', 'yaml'])  # noqa: E501
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        add_file_common_args=True,
    )

    file_args = module.load_file_common_arguments(module.params)

    # Gather module parameters in variables
    state = module.params['state']
    name = module.params.get('name')
    caps = module.params.get('caps')
    secret = module.params.get('secret')
    import_key = module.params.get('import_key')
    dest = module.params.get('dest')
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
    _secret = secret
    _caps = caps
    key_exist = 1

    if (state in ["present", "update"]):
        # if dest is not a directory, the user wants to change the file's name
        # (e,g: /etc/ceph/ceph.mgr.ceph-mon2.keyring)
        if not os.path.isdir(dest):
            file_path = dest
        else:
            keyring_filename = "ceph" + "." + name + ".keyring"
            file_path = os.path.join(dest, keyring_filename)

        file_args['path'] = file_path

        if import_key:
            _info_key = []
            rc, cmd, out, err = exec_commands(
                module, info_key(name, output_format))  # noqa: E501
            key_exist = rc
            if not caps and key_exist != 0:
                fatal("Capabilities must be provided when state is 'present'", module)  # noqa: E501
            if key_exist != 0 and secret is None and caps is None:
                fatal("Keyring doesn't exist, you must provide 'secret' and 'caps'", module)  # noqa: E501
            if key_exist == 0:
                _info_key = json.loads(out)
                if not secret:
                    secret = _info_key[0]['key']
                _secret = _info_key[0]['key']
                if not caps:
                    caps = _info_key[0]['caps']
                _caps = _info_key[0]['caps']
                if secret == _secret and caps == _caps:
                    if not os.path.isfile(file_path):
                        rc, cmd, out, err = exec_commands(module, get_key(name, file_path))  # noqa: E501
                        result["rc"] = rc
                        if rc != 0:
                            result["stdout"] = "Couldn't fetch the key {0} at {1}.".format(name, file_path)  # noqa: E501
                            module.exit_json(**result)
                        result["stdout"] = "fetched the key {0} at {1}.".format(name, file_path)  # noqa: E501

                    result["stdout"] = "{0} already exists and doesn't need to be updated.".format(name)  # noqa: E501
                    result["rc"] = 0
                    module.set_fs_attributes_if_different(file_args, False)
                    module.exit_json(**result)
        else:
            if os.path.isfile(file_path) and not secret or not caps:
                result["stdout"] = "{0} already exists in {1} you must provide secret *and* caps when import_key is {2}".format(name, dest, import_key)  # noqa: E501
                result["rc"] = 0
                module.exit_json(**result)
        if (key_exist == 0 and (secret != _secret or caps != _caps)) or key_exist != 0:  # noqa: E501
            rc, cmd, out, err = exec_commands(module, create_key(
                module, result, name, secret, caps, import_key, file_path))  # noqa: E501
            if rc != 0:
                result["stdout"] = "Couldn't create or update {0}".format(name)
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

    elif state == "generate_secret":
        out = generate_secret().decode()
        cmd = ''
        rc = 0
        err = ''
        changed = True

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
        changed=changed,
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
