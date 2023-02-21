
from scaleway import Client
from scaleway.secret.v1alpha1.api import (AccessSecretVersionResponse, Secret,
                                          SecretV1Alpha1API)


class ScalewaySecret():
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
        data = self.secret.access_secret_version(secret_id=secret_id, revision=last_updated_enabled_version).data

        return data

    def access_secret_version_by_revision(self, secret_id, revision) -> AccessSecretVersionResponse:
        """Return the secret version of a secret"""
        data = self.secret.access_secret_version(secret_id=secret_id, revision=revision).data
        return data

    def get_secret_by_name(self, name: str,  project_id: str = None) -> Secret | None:       
        """Return the secret version of a secret"""
        for i in self.secret.list_secrets().secrets:
            if i.name == name:
                return i
        return None

    def access_secret_version_by_name(self, secret_name) -> AccessSecretVersionResponse:
        """Return the secret version of a secret"""
        secret_id = self.get_secret_by_name(secret_name)
        data = self.access_secret_last_updated_enabled_version(secret_id)
        data = self.secret.access_secret_version(secret_id=secret_name)
        return data
