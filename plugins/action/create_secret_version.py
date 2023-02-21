# from secret import ScalewaySecret
from collections import OrderedDict

from ansible.module_utils.basic import AnsibleModule
from scaleway import Client
from scaleway.secret.v1alpha1.api import (AccessSecretVersionResponse, Secret,
                                          SecretV1Alpha1API, SecretVersion)


def main():

    
    # secret = MySecret()
    # secret = ScalewaySecret()
    client = Client.from_config_file_and_env()
    secret = SecretV1Alpha1API(client)
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        secret_id=dict(type='str',required=False),
        name=dict(type='str',required=False),
        project_id=dict(type='str', required=False)
        #  module.params.has_key("secret_id"):    
        data=dict(type='str', required=True),
    )
    mutually_exclusive_args = [('secret_id'),('secret_name')]
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    data = module.params['data']
    print(module.params)
    if  module.params['secret_id']:
        result['changed'] = True
        secret_id =  module.params['secret_id']
        name = secret.get_secret(secret_id=secret_id).name
        # my_result =  secret.create_secret_version(secret_id=secret_id, data=secret_value)
    else:
        name = module.params['name'] 
        secret_id = secret.create_secret(name=name)
        print(secret_id)

    secret_version = secret.create_secret_version(secret_id=secret_id, data=data)

    # elif "name" in module.params:
    #     #  module.params.has_key("secret_id"):    
    #     result['changed'] = True
    #     secret_name =  module.params['name']
    #     my_result =  secret.access_secret_last_updated_enabled_version(secret_id)
        
    result['message'] =  OrderedDict( {'secret_name':name,'secret_id': secret_version.secret_id,
                                        'revision': secret_version.revision} )

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

# if __name__ == '__main__':
#     main()

# class ActionModule(ActionBase):
#     """Action plugin to retrieve secrets from a secret manager"""
#     def run(self, tmp=None, task_vars=None):
#         super(ActionModule, self).run(tmp, task_vars)
#         secret_id = self._task.args.get('secret_id')
#         secret = MySecret()
#         return secret.access_secret_last_updated_enabled_version(secret_id)


# def main():
#   """Main function"""
#   module = AnsibleModule(
#         argument_spec=dict(
#             secret_id=dict(type='str', required=True),
#         )
#     )
#   secret = ActionModule.run(module.params)
#   module.exit_json(secret=secret)

if __name__ == '__main__':
    main()
