# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from . import cephadm_test_common
from ansible_collections.stackhpc.cephadm.plugins.modules import cephadm_crush_rule
from mock.mock import patch

fake_cluster = 'ceph'
fake_name = 'foo'
fake_bucket_root = 'default'
fake_bucket_type = 'host'
fake_device_class = 'ssd'
fake_profile = 'default'
fake_user = 'client.admin'
fake_keyring = '/etc/ceph/{0}.{1}.keyring'.format(fake_cluster, fake_user)


class TestCephCrushRuleModule(object):

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    def test_without_parameters(self, m_fail_json):
        cephadm_test_common.set_module_args({})
        m_fail_json.side_effect = cephadm_test_common.fail_json

        with pytest.raises(cephadm_test_common.AnsibleFailJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['msg'] == 'missing required arguments: name'

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    def test_with_name_only(self, m_fail_json):
        cephadm_test_common.set_module_args({
            'name': fake_name
        })
        m_fail_json.side_effect = cephadm_test_common.fail_json

        with pytest.raises(cephadm_test_common.AnsibleFailJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['msg'] == 'state is present but all of the following are missing: rule_type'

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    def test_with_check_mode(self, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type,
            '_ansible_check_mode': True
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['rc'] == 0
        assert not result['stdout']
        assert not result['stderr']

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_non_existing_replicated_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        get_rc = 2
        get_stderr = 'Error ENOENT: unknown crush rule \'{0}\''.format(fake_name)
        get_stdout = ''
        create_rc = 0
        create_stderr = ''
        create_stdout = ''
        m_run_command.side_effect = [
            (get_rc, get_stdout, get_stderr),
            (create_rc, create_stdout, create_stderr)
        ]

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule',
                                 'create-replicated', fake_name, fake_bucket_root, fake_bucket_type]
        assert result['rc'] == create_rc
        assert result['stderr'] == create_stderr
        assert result['stdout'] == create_stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_existing_replicated_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 0
        stderr = ''
        stdout = '{{"rule_name":"{0}","type":1,"steps":[{{"item_name":"{1}"}},{{"type":"{2}"}}]}}'.format(fake_name, fake_bucket_root, fake_bucket_type)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']
        assert result['rc'] == 0
        assert result['stderr'] == stderr
        assert result['stdout'] == stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_non_existing_replicated_rule_device_class(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type,
            'device_class': fake_device_class
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        get_rc = 2
        get_stderr = 'Error ENOENT: unknown crush rule \'{0}\''.format(fake_name)
        get_stdout = ''
        create_rc = 0
        create_stderr = ''
        create_stdout = ''
        m_run_command.side_effect = [
            (get_rc, get_stdout, get_stderr),
            (create_rc, create_stdout, create_stderr)
        ]

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule',
                                 'create-replicated', fake_name, fake_bucket_root, fake_bucket_type, fake_device_class]
        assert result['rc'] == create_rc
        assert result['stderr'] == create_stderr
        assert result['stdout'] == create_stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_existing_replicated_rule_device_class(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type,
            'device_class': fake_device_class
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 0
        stderr = ''
        stdout = '{{"rule_name":"{0}","type":1,"steps":[{{"item_name":"{1}"}},{{"type":"{2}"}}]}}'.format(fake_name, fake_bucket_root, fake_bucket_type)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']
        assert result['rc'] == 0
        assert result['stderr'] == stderr
        assert result['stdout'] == stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_non_existing_erasure_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'erasure',
            'profile': fake_profile
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        get_rc = 2
        get_stderr = 'Error ENOENT: unknown crush rule \'{0}\''.format(fake_name)
        get_stdout = ''
        create_rc = 0
        create_stderr = ''
        create_stdout = 'created rule {0} at 1'.format(fake_name)
        m_run_command.side_effect = [
            (get_rc, get_stdout, get_stderr),
            (create_rc, create_stdout, create_stderr)
        ]

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'create-erasure', fake_name, fake_profile]
        assert result['rc'] == create_rc
        assert result['stderr'] == create_stderr
        assert result['stdout'] == create_stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_create_existing_erasure_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'erasure',
            'profile': fake_profile
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 0
        stderr = ''
        stdout = '{{"type":3,"rule_name":"{0}","steps":[{{"item_name":"default"}},{{"type":"host"}}]}}'.format(fake_name)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']
        assert result['rc'] == 0
        assert result['stderr'] == stderr
        assert result['stdout'] == stdout

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_update_existing_replicated_rule(self, m_run_command, m_fail_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'replicated',
            'bucket_root': fake_bucket_root,
            'bucket_type': fake_bucket_type,
            'device_class': fake_device_class
        })
        m_fail_json.side_effect = cephadm_test_common.fail_json
        rc = 0
        stderr = ''
        stdout = '{{"type":3,"rule_name":"{0}","steps":[{{"item_name":"default"}},{{"type":"host"}}]}}'.format(fake_name)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleFailJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['msg'] == 'Can not convert crush rule {0} to replicated'.format(fake_name)
        assert result['rc'] == 1

    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_update_existing_erasure_rule(self, m_run_command, m_fail_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'rule_type': 'erasure',
            'profile': fake_profile
        })
        m_fail_json.side_effect = cephadm_test_common.fail_json
        rc = 0
        stderr = ''
        stdout = '{{"type":1,"rule_name":"{0}","steps":[{{"item_name":"default"}},{{"type":"host"}}]}}'.format(fake_name)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleFailJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['msg'] == 'Can not convert crush rule {0} to erasure'.format(fake_name)
        assert result['rc'] == 1

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_remove_non_existing_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'state': 'absent'
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 2
        stderr = 'Error ENOENT: unknown crush rule \'{0}\''.format(fake_name)
        stdout = ''
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']
        assert result['rc'] == 0
        assert result['stderr'] == stderr
        assert result['stdout'] == "Crush Rule {0} doesn't exist".format(fake_name)

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_remove_existing_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'state': 'absent'
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        get_rc = 0
        get_stderr = ''
        get_stdout = '{{"rule_name":"{0}","steps":[{{"item_name":"{1}"}},{{"type":"{2}"}}]}}'.format(fake_name, fake_bucket_root, fake_bucket_type)
        remove_rc = 0
        remove_stderr = ''
        remove_stdout = ''
        m_run_command.side_effect = [
            (get_rc, get_stdout, get_stderr),
            (remove_rc, remove_stdout, remove_stderr)
        ]

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'rm', fake_name]
        assert result['rc'] == remove_rc
        assert result['stderr'] == remove_stderr
        assert result['stdout'] == remove_stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_get_non_existing_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'state': 'info'
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 2
        stderr = 'Error ENOENT: unknown crush rule \'{0}\''.format(fake_name)
        stdout = ''
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']

        assert result['rc'] == rc
        assert result['stderr'] == stderr
        assert result['stdout'] == stdout

    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('ansible.module_utils.basic.AnsibleModule.run_command')
    def test_get_existing_rule(self, m_run_command, m_exit_json):
        cephadm_test_common.set_module_args({
            'name': fake_name,
            'state': 'info'
        })
        m_exit_json.side_effect = cephadm_test_common.exit_json
        rc = 0
        stderr = ''
        stdout = '{{"rule_name":"{0}","steps":[{{"item_name":"{1}"}},{{"type":"{2}"}}]}}'.format(fake_name, fake_bucket_root, fake_bucket_type)
        m_run_command.return_value = rc, stdout, stderr

        with pytest.raises(cephadm_test_common.AnsibleExitJson) as result:
            cephadm_crush_rule.main()

        result = result.value.args[0]
        assert not result['changed']
        assert result['cmd'] == ['cephadm', '--timeout', '60', 'shell', '--', 'ceph',
                                 'osd', 'crush', 'rule', 'dump', fake_name, '--format=json']

        assert result['rc'] == rc
        assert result['stderr'] == stderr
        assert result['stdout'] == stdout
