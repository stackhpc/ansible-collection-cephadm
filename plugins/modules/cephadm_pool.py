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
module: cephadm_pool
author:
    - Guillaume Abrioux <gabrioux@redhat.com>
    - Michal Nasiadka <michal@stackhpc.com>
short_description: Manage Ceph Pools
version_added: "1.4.0"
description:
    - Manage Ceph pool(s) creation, deletion and updates.
options:
    name:
        description:
            - name of the Ceph pool
        required: true
        type: str
    state:
        description:
            - If 'present' is used, the module creates a pool if it doesn't
              exist or update it if it already exists.
              If 'absent' is used, the module will simply delete the pool.
              If 'list' is used, the module will return all details about the
              existing pools. (json formatted).
        required: false
        choices: ['present', 'absent', 'list']
        default: present
        type: str
    details:
        description:
            - show details when state is list
        required: false
        type: bool
    size:
        description:
            - set the replica size of the pool.
        required: false
        type: str
    min_size:
        description:
            - set the min_size parameter of the pool.
        required: false
        default: default to `osd_pool_default_min_size` (ceph)
        type: str
    pg_num:
        description:
            - set the pg_num of the pool.
        required: false
        default: default to `osd_pool_default_pg_num` (ceph)
        type: str
    pgp_num:
        description:
            - set the pgp_num of the pool.
        required: false
        default: default to `osd_pool_default_pgp_num` (ceph)
        type: str
    pg_autoscale_mode:
        description:
            - set the pg autoscaler on the pool.
        required: false
        default: 'on'
        type: str
    target_size_ratio:
        description:
            - set the target_size_ratio on the pool
        required: false
        type: str
    pool_type:
        description:
            - set the pool type, either 'replicated' or 'erasure'
        required: false
        default: replicated
        choices: ['replicated', 'erasure']
        type: str
    erasure_profile:
        description:
            - When pool_type = 'erasure', set the erasure profile of the pool
        required: false
        default: default
        type: str
    rule_name:
        description:
            - Set the crush rule name assigned to the pool
        required: false
        type: str
    expected_num_objects:
        description:
            - Set the expected_num_objects parameter of the pool.
        required: false
        default: "0"
        type: str
    application:
        description:
            - Set the pool application on the pool.
        required: false
        default: None
        type: str
    allow_ec_overwrites:
        description:
            - Set the allow_ec_overwrites paramter of the pool.
        required: false
        default: false
        type: bool
'''

EXAMPLES = r'''
- hosts: all
  become: true
  tasks:
    - name: create a pool
      ceph_pool:
        name: "{{ item.name }}"
        state: present
        size: "{{ item.size }}"
        application: "{{ item.application }}"
        pool_type: "{{ item.pool_type }}"
        pg_autoscale_mode: "{{ item.pg_autoscale_mode }}"
      with_items: "{{ pools }}"
'''

RETURN = r'''#  '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stackhpc.cephadm.plugins.module_utils.cephadm_common \
    import generate_ceph_cmd, exec_command, exit_module

import datetime
import json


def check_pool_exist(name,
                     output_format='json'):
    '''
    Check if a given pool exists
    '''

    args = ['stats', name, '-f', output_format]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def get_application_pool(name,
                         output_format='json'):
    '''
    Get application type enabled on a given pool
    '''

    args = ['application', 'get', name, '-f', output_format]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def enable_application_pool(name,
                            application):
    '''
    Enable application on a given pool
    '''

    args = ['application', 'enable', name, application]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def disable_application_pool(name,
                             application):
    '''
    Disable application on a given pool
    '''

    args = ['application', 'disable', name,
            application, '--yes-i-really-mean-it']

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def get_pool_ec_overwrites(name, output_format='json'):
    '''
    Get EC overwrites on a given pool
    '''

    args = ['get', name, 'allow_ec_overwrites',
            '-f', output_format]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def enable_ec_overwrites(name):
    '''
    Enable EC overwrites on a given pool
    '''

    args = ['set', name, 'allow_ec_overwrites',
            'true']

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def disable_ec_overwrites(name):
    '''
    Disable EC overwrites on a given pool
    '''

    args = ['set', name, 'allow_ec_overwrites',
            'false']

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def get_pool_details(module,
                     name,
                     output_format='json'):
    '''
    Get details about a given pool
    '''

    args = ['ls', 'detail', '-f', output_format]

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    rc, cmd, out, err = exec_command(module, cmd)

    if rc == 0:
        out = [p for p in json.loads(out.strip()) if p['pool_name'] == name][0]

    _rc, _cmd, application_pool, _err = exec_command(module,
                                                     get_application_pool(name)
                                                     )

    # This is a trick because "target_size_ratio" isn't present at the same
    # level in the dict
    # ie:
    # {
    # 'pg_num': 8,
    # 'pgp_num': 8,
    # 'pg_autoscale_mode': 'on',
    #     'options': {
    #          'target_size_ratio': 0.1
    #     }
    # }
    # If 'target_size_ratio' is present in 'options', we set it, this way we
    # end up with a dict containing all needed keys at the same level.
    if 'target_size_ratio' in out['options'].keys():
        out['target_size_ratio'] = out['options']['target_size_ratio']
    else:
        out['target_size_ratio'] = None

    application = list(json.loads(application_pool.strip()).keys())

    if len(application) == 0:
        out['application'] = ''
    else:
        out['application'] = application[0]

    return rc, cmd, out, err


def compare_pool_config(user_pool_config, running_pool_details):
    '''
    Compare user input config pool details with current running pool details
    '''

    delta = {}
    filter_keys = ['pg_num', 'pg_placement_num', 'size',
                   'pg_autoscale_mode', 'target_size_ratio']
    for key in filter_keys:
        if (str(running_pool_details[key]) != user_pool_config[key]['value'] and  # noqa: E501
                user_pool_config[key]['value']):
            delta[key] = user_pool_config[key]

    if (running_pool_details['application'] !=
            user_pool_config['application']['value'] and
            user_pool_config['application']['value']):
        delta['application'] = {}
        delta['application']['new_application'] = user_pool_config['application']['value']  # noqa: E501
        # to be improved (for update_pools()...)
        delta['application']['value'] = delta['application']['new_application']
        delta['application']['old_application'] = running_pool_details['application']  # noqa: E501

    return delta


def list_pools(details,
               output_format='json'):
    '''
    List existing pools
    '''

    args = ['ls']

    if details:
        args.append('detail')

    args.extend(['-f', output_format])

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def create_pool(name,
                user_pool_config):
    '''
    Create a new pool
    '''

    args = ['create', user_pool_config['pool_name']['value'],
            user_pool_config['type']['value']]

    if user_pool_config['pg_autoscale_mode']['value'] != 'on':
        args.extend(['--pg_num',
                     user_pool_config['pg_num']['value'],
                     '--pgp_num',
                     user_pool_config['pgp_num']['value']])
    elif user_pool_config['target_size_ratio']['value']:
        args.extend(['--target_size_ratio',
                     user_pool_config['target_size_ratio']['value']])

    if user_pool_config['type']['value'] == 'replicated':
        args.extend([user_pool_config['crush_rule']['value'],
                     '--expected_num_objects',
                     user_pool_config['expected_num_objects']['value'],
                     '--autoscale-mode',
                     user_pool_config['pg_autoscale_mode']['value']])

    if (user_pool_config['size']['value'] and
            user_pool_config['type']['value'] == "replicated"):
        args.extend(['--size', user_pool_config['size']['value']])

    elif user_pool_config['type']['value'] == 'erasure':
        args.extend([user_pool_config['erasure_profile']['value']])

        if user_pool_config['crush_rule']['value']:
            args.extend([user_pool_config['crush_rule']['value']])

        args.extend(['--expected_num_objects',
                     user_pool_config['expected_num_objects']['value'],
                     '--autoscale-mode',
                     user_pool_config['pg_autoscale_mode']['value']])

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def remove_pool(name):
    '''
    Remove a pool
    '''

    args = ['rm', name, name, '--yes-i-really-really-mean-it']

    cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                            args=args)

    return cmd


def update_pool(module, name, delta):
    '''
    Update an existing pool
    '''

    report = ""

    for key in delta.keys():
        if key != 'application':
            args = ['set',
                    name,
                    delta[key]['cli_set_opt'],
                    delta[key]['value']]

            cmd = generate_ceph_cmd(sub_cmd=['osd', 'pool'],
                                    args=args)

            rc, cmd, out, err = exec_command(module, cmd)
            if rc != 0:
                return rc, cmd, out, err

        else:
            rc, cmd, out, err = exec_command(module, disable_application_pool(name, delta['application']['old_application']))  # noqa: E501
            if rc != 0:
                return rc, cmd, out, err

            rc, cmd, out, err = exec_command(module, enable_application_pool(name, delta['application']['new_application']))  # noqa: E501
            if rc != 0:
                return rc, cmd, out, err

        report = report + "\n" + "{0} has been updated: {1} is now {2}".format(name, key, delta[key]['value'])  # noqa: E501

    out = report
    return rc, cmd, out, err


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', required=False, default='present',
                   choices=['present', 'absent', 'list']),
        details=dict(type='bool', required=False, default=False),
        size=dict(type='str', required=False),
        min_size=dict(type='str', required=False),
        pg_num=dict(type='str', required=False),
        pgp_num=dict(type='str', required=False),
        pg_autoscale_mode=dict(type='str', required=False, default='on'),
        target_size_ratio=dict(type='str', required=False, default=None),
        pool_type=dict(type='str', required=False, default='replicated',
                       choices=['replicated', 'erasure']),
        erasure_profile=dict(type='str', required=False, default='default'),
        rule_name=dict(type='str', required=False, default=None),
        expected_num_objects=dict(type='str', required=False, default="0"),
        application=dict(type='str', required=False, default=None),
        allow_ec_overwrites=dict(type='bool', required=False, default=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Gather module parameters in variables
    name = module.params.get('name')
    state = module.params.get('state')
    details = module.params.get('details')
    size = module.params.get('size')
    min_size = module.params.get('min_size')
    pg_num = module.params.get('pg_num')
    pgp_num = module.params.get('pgp_num')
    pg_autoscale_mode = module.params.get('pg_autoscale_mode')
    target_size_ratio = module.params.get('target_size_ratio')
    application = module.params.get('application')
    allow_ec_overwrites = module.params.get('allow_ec_overwrites')

    if (module.params.get('pg_autoscale_mode').lower() in
            ['true', 'on', 'yes']):
        pg_autoscale_mode = 'on'
    elif (module.params.get('pg_autoscale_mode').lower() in
          ['false', 'off', 'no']):
        pg_autoscale_mode = 'off'
    else:
        pg_autoscale_mode = 'warn'

    if module.params.get('pool_type') == '1':
        pool_type = 'replicated'
    elif module.params.get('pool_type') == '3':
        pool_type = 'erasure'
    else:
        pool_type = module.params.get('pool_type')

    if not module.params.get('rule_name'):
        rule_name = 'replicated_rule' if pool_type == 'replicated' else None
    else:
        rule_name = module.params.get('rule_name')

    erasure_profile = module.params.get('erasure_profile')
    expected_num_objects = module.params.get('expected_num_objects')
    user_pool_config = {
        'pool_name': {'value': name},
        'pg_num': {'value': pg_num, 'cli_set_opt': 'pg_num'},
        'pgp_num': {'value': pgp_num, 'cli_set_opt': 'pgp_num'},
        'pg_autoscale_mode': {'value': pg_autoscale_mode,
                              'cli_set_opt': 'pg_autoscale_mode'},
        'target_size_ratio': {'value': target_size_ratio,
                              'cli_set_opt': 'target_size_ratio'},
        'application': {'value': application},
        'type': {'value': pool_type},
        'erasure_profile': {'value': erasure_profile},
        'crush_rule': {'value': rule_name, 'cli_set_opt': 'crush_rule'},
        'expected_num_objects': {'value': expected_num_objects},
        'size': {'value': size, 'cli_set_opt': 'size'},
        'min_size': {'value': min_size},
        'allow_ec_overwrites': {'value': allow_ec_overwrites}
    }

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
        rc, cmd, out, err = exec_command(module,
                                         check_pool_exist(name))
        if rc == 0:
            running_pool_details = get_pool_details(module,
                                                    name)
            user_pool_config['pg_placement_num'] = {'value': str(running_pool_details[2]['pg_placement_num']), 'cli_set_opt': 'pgp_num'}  # noqa: E501
            delta = compare_pool_config(user_pool_config,
                                        running_pool_details[2])

            if user_pool_config['type']['value'] == 'erasure':
                rc, cmd, ec_overwrites, err = exec_command(module, get_pool_ec_overwrites(name))  # noqa: E501
                running_pool_ec_overwrites = json.loads(ec_overwrites.strip()).get('allow_ec_overwrites')  # noqa: E501
                if running_pool_ec_overwrites != user_pool_config['allow_ec_overwrites']['value']:  # noqa: E501
                    if user_pool_config['allow_ec_overwrites']['value']:
                        rc, cmd, out, err = exec_command(module, enable_ec_overwrites(name))  # noqa: E501
                    else:
                        rc, cmd, out, err = exec_command(module, disable_ec_overwrites(name))  # noqa: E501
                    if rc == 0:
                        changed = True

            if len(delta) > 0:
                keys = list(delta.keys())
                details = running_pool_details[2]
                if details['erasure_code_profile'] and 'size' in keys:
                    del delta['size']
                if details['pg_autoscale_mode'] == 'on':
                    delta.pop('pg_num', None)
                    delta.pop('pgp_num', None)

                if len(delta) == 0:
                    out = "Skipping pool {0}.\nUpdating either 'size' on an erasure-coded pool or 'pg_num'/'pgp_num' on a pg autoscaled pool is incompatible".format(name)  # noqa: E501
                else:
                    rc, cmd, out, err = update_pool(module,
                                                    name,
                                                    delta)
                    if rc == 0:
                        changed = True

            else:
                out = "Pool {0} already exists and there is nothing to update.".format(name)  # noqa: E501
        else:
            rc, cmd, out, err = exec_command(module,
                                             create_pool(name,
                                                         user_pool_config=user_pool_config))  # noqa: E501
            if user_pool_config['application']['value']:
                rc, _, _, _ = exec_command(module,
                                           enable_application_pool(name,
                                                                   user_pool_config['application']['value']))  # noqa: E501
            if user_pool_config['min_size']['value']:
                # not implemented yet
                pass
            if user_pool_config['allow_ec_overwrites']['value']:
                rc, _, _, _ = exec_command(module,
                                           enable_ec_overwrites(name))

            changed = True

    elif state == "list":
        rc, cmd, out, err = exec_command(module,
                                         list_pools(name,
                                                    details))
        if rc != 0:
            out = "Couldn't list pool(s) present on the cluster"

    elif state == "absent":
        rc, cmd, out, err = exec_command(module,
                                         check_pool_exist(name))
        if rc == 0:
            rc, cmd, out, err = exec_command(module,
                                             remove_pool(name))
            changed = True
        else:
            rc = 0
            out = "Skipped, since pool {0} doesn't exist".format(name)

    exit_module(module=module, out=out, rc=rc, cmd=cmd, err=err, startd=startd,
                changed=changed)


def main():
    run_module()


if __name__ == '__main__':
    main()
