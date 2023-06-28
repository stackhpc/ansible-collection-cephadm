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


DOCUMENTATION = '''
---
module: cephadm_ec_profile

short_description: Manage Ceph Erasure Code profile

version_added: "1.4.0"

description:
    - Manage Ceph Erasure Code profile
options:
    name:
        description:
            - name of the profile.
        required: true
        type: str
    state:
        description:
            If 'present' is used, the module creates a profile.
            If 'absent' is used, the module will delete the profile.
        required: false
        choices: ['present', 'absent']
        default: present
        type: str
    stripe_unit:
        description:
            - The amount of data in a data chunk, per stripe.
        required: false
        type: str
    k:
        description:
            - Number of data-chunks the object will be split in
        required: false
        type: str
    m:
        description:
            - Compute coding chunks for each object and store them on different
              OSDs.
        required: false
        type: str
    plugin:
        description:
            - Use the erasure code plugin to compute coding chunks and recover
              missing chunks.
        required: false
        type: str
    directory:
        description:
            - Set the directory name from which the erasure code plugin is
              loaded.
        required: false
        type: str
    crush_device_class:
        description:
            - Restrict placement to devices of a specific class (hdd/ssd)
        required: false
        type: str

author:
    - Guillaume Abrioux <gabrioux@redhat.com>
    - Michal Nasiadka <michal@stackhpc.com>
'''

EXAMPLES = '''
- name: create an erasure code profile
  cephadm_ec_profile:
    name: foo
    k: 4
    m: 2

- name: delete an erasure code profile
  cephadm_ec_profile:
    name: foo
    state: absent
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stackhpc.cephadm.plugins.module_utils.cephadm_common \
    import generate_ceph_cmd, exec_command, exit_module

import datetime
import json


RETURN = '''#  '''


def get_profile(module, name):
    '''
    Get existing profile
    '''

    args = ['get', name, '--format=json']

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'erasure-code-profile'],
                            args=args)

    return cmd


def create_profile(module, name, k, m, stripe_unit, crush_device_class, directory, plugin, force=False):  # noqa: E501
    '''
    Create a profile
    '''

    args = ['set', name, 'k={0}'.format(k), 'm={0}'.format(m)]
    if stripe_unit:
        args.append('stripe_unit={0}'.format(stripe_unit))
    if crush_device_class:
        args.append('crush-device-class={0}'.format(crush_device_class))
    if directory:
        args.append('directory={0}'.format(plugin))
    if plugin:
        args.append('plugin={0}'.format(plugin))
    if force:
        args.append('--force')

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'erasure-code-profile'],
                            args=args)

    return cmd


def delete_profile(module, name):
    '''
    Delete a profile
    '''

    args = ['rm', name]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'erasure-code-profile'],
                            args=args)

    return cmd


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=False,
                   choices=['present', 'absent'], default='present'),
        stripe_unit=dict(type='str', required=False),
        k=dict(type='str', required=False),
        m=dict(type='str', required=False),
        crush_device_class=dict(type='str', required=False),
        directory=dict(type='str', required=False),
        plugin=dict(type='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[['state', 'present', ['k', 'm']]],
    )

    # Gather module parameters in variables
    name = module.params.get('name')
    state = module.params.get('state')
    stripe_unit = module.params.get('stripe_unit')
    k = module.params.get('k')
    m = module.params.get('m')
    crush_device_class = module.params.get('crush_device_class')
    directory = module.params.get('directory')
    plugin = module.params.get('plugin')

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
        rc, cmd, out, err = exec_command(module, get_profile(module, name))  # noqa: E501
        if rc == 0:
            # the profile already exists, let's check whether we have to
            # update it
            current_profile = json.loads(out)
            if current_profile['k'] != k or \
               current_profile['m'] != m or \
               current_profile.get('stripe_unit', stripe_unit) != stripe_unit or \
               current_profile.get('crush-device-class', crush_device_class) != crush_device_class or \
               current_profile.get('directory', directory) != directory or \
               current_profile.get('plugin', plugin) != plugin:  # noqa: E501
                rc, cmd, out, err = exec_command(module,
                                                 create_profile(module,
                                                                name,
                                                                k,
                                                                m,
                                                                stripe_unit,
                                                                crush_device_class,  # noqa: E501
                                                                directory,
                                                                plugin,
                                                                force=True))  # noqa: E501
                changed = True
        else:
            # the profile doesn't exist, it has to be created
            rc, cmd, out, err = exec_command(module, create_profile(module,
                                                                    name,
                                                                    k,
                                                                    m,
                                                                    stripe_unit,  # noqa: E501
                                                                    crush_device_class,  # noqa: E501
                                                                    directory,
                                                                    plugin))
            if rc == 0:
                changed = True

    elif state == "absent":
        rc, cmd, out, err = exec_command(module, delete_profile(module, name))  # noqa: E501
        if not err:
            out = 'Profile {0} removed.'.format(name)
            changed = True
        else:
            rc = 0
            out = "Skipping, the profile {0} doesn't exist".format(name)

    exit_module(module=module, out=out, rc=rc, cmd=cmd, err=err, startd=startd, changed=changed)  # noqa: E501


def main():
    run_module()


if __name__ == '__main__':
    main()
