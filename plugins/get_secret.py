import ansible.module_utils.common.yaml
import ansible.module_utils.compat.importlib
import ansible.module_utils.compat.typing
import ansible.module_utils.compat.version
from ansible.errors import AnsibleError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common import *
from ansible.plugins.action import ActionBase
from scaleway import Client
from scaleway.secret.v1alpha1.api import (AccessSecretVersionResponse, Secret,
                                          SecretV1Alpha1API)

# from keeper_secrets_manager_ansible import KeeperAnsible

DOCUMENTATION = r'''
---
module: get_secret
short_description: Get value(s) from the Keeper Vault
version_added: "1.0.0"
description:
    - Copy a value from the Scaleway Secret Manager into a variable.
author:
    - Fabrice Sodogandji
options:
  uid:
    description:
    - The UUID of the scaleway secret.
    type: str
    required: no
  field:
    description:
    - The label, or type, of the standard field in record that contains the value.
    - If the value has a complex value, use notation to get the specific value from the complex value.
    type: str
    required: no
'''

EXAMPLES = r'''
- name: Get login name
  get_secret:
    uid: 5E20B724-72C9-4778-9BC5-059075D9936E
  register: my_secret_value
'''

RETURN = r'''
value:
  description: The secret value
  returned: success
  my_secret_value: |
      {
        "login": "foo",
        "password": "bar"
      }
'''
class MySecret():
    """ A class containing  common method used by the Ansible plugin and also talked to Scaleway Python SDK
    """
    
    def __init__(self,  **kwargs):
        # self.secret = secret
        self.kwargs = kwargs
        self.client = Client.from_config_file_and_env()
        self.secret = SecretV1Alpha1API(self.client)

    def get_secret_api(self) -> SecretV1Alpha1API:
        """Return the secret API"""
        return SecretV1Alpha1API(self.client)

    def get_list_enabled_version(self, secret_id) -> list[int]:
        """Return the list of enabled version of a secret"""
        list_secret_version  = self.secret.list_secret_versions(secret_id=secret_id)
        lv =[ (i.secret_id, i.revision,i.status, i.updated_at) for i in list_secret_version.versions]
        print('LV: ',lv)
        return [i[1] for i in lv if i[2] == "enabled"]

    def get_secret_version_by_revision(self, secret_id, revision):
        """Return the secret version of a secret"""
        s = self.secret.get_secret_version(secret_id=secret_id, revision=revision)
        return s

    def get_secret_last_updated_enabled_version(self, secret_id)  -> int:
        """Return the last updated enabled version of a secret"""
        list_secret_version  = self.secret.list_secret_versions(secret_id=secret_id)
        lv =[ (i.secret_id, i.revision,i.status, i.updated_at) for i in list_secret_version.versions]
        print('LV: ',lv)
        lv = [i for i in lv if i[2] == "enabled"]
        lv.sort(key=lambda x: x[3], reverse=True)
        return lv[0][1]

    def access_secret_last_updated_enabled_version(self, secret_id) -> AccessSecretVersionResponse:
        """Return the last updated enabled version of a secret"""
        last_updated_enabled_version = self.get_secret_last_updated_enabled_version(secret_id)
        data = self.secret.access_secret_version(secret_id=secret_id, revision=last_updated_enabled_version)

        return data

    def access_secret_version_by_revision(self, secret_id, revision) -> AccessSecretVersionResponse:
        """Return the secret version of a secret"""
        data = self.secret.access_secret_version(secret_id=secret_id, revision=revision)
        return data

    def get_secret_by_name(self, name: str, secret: SecretV1Alpha1API, project_id: str = None) -> Secret | None:       
        """Return the secret version of a secret"""
        for i in secret.list_secrets().secrets:
            if i.name == name:
                return i
        return None


    def access_secret_version_by_name(self, secret_name) -> AccessSecretVersionResponse:
        """Return the secret version of a secret"""
        data = self.secret.access_secret_version(secret_id=secret_name)
        return data

# class ActionModule(ActionBase):

#     def run(self, tmp=None, task_vars=None):
#         super(ActionModule, self).run(tmp, task_vars)

#         if task_vars is None:
#             task_vars = {}

#         keeper = KeeperAnsible(task_vars=task_vars)

#         if self._task.args.get("notation") is not None:
#             value = keeper.get_value_via_notation(self._task.args.get("notation"))
#         else:
#             uid = self._task.args.get("uid")
#             if uid is None:
#                 raise AnsibleError("The uid is blank. keeper_get requires this value to be set.")

#             # Try to get either the field, custom_field, or file name.
#             field_type_enum, field_key = keeper.get_field_type_enum_and_key(args=self._task.args)

#             allow_array = self._task.args.get("allow_array", False)
#             value = keeper.get_value(uid, field_type=field_type_enum, key=field_key, allow_array=allow_array)

#         keeper.stash_secret_value(value)

#         result = {
#             "value": value
#         }

#         keeper.add_secret_values_to_results(result)

#         return result



class ActionModule(ActionBase):
    """Action plugin to retrieve secrets from a secret manager"""
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        secret_id = self._task.args.get('secret_id')
        secret = MySecret()
        return secret.access_secret_last_updated_enabled_version(secret_id)


def main():
  """Main function"""
  module = AnsibleModule(
        argument_spec=dict(
            secret_id=dict(type='str', required=True),
        )
    )
  secret = ActionModule.run(module.params)
  module.exit_json(secret=secret)

if __name__ == '__main__':
    main()
