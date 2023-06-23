from dataclasses import dataclass

__all__ = ['TerraformModuleIdentifier']


@dataclass()
class TerraformModuleIdentifier:
    """Define a Terraform Module Identifier.

    Attributes:

        namespace (str): is the name of a namespace, unique on a particular hostname,
            that can contain one or more modules that are somehow related.
        name (str):  the module name
        system (str): the name of a remote system that the module is primarily written to target,
            like aws or azurerm
    """

    namespace: str
    name: str
    system: str

    @property
    def module_id(self) -> str:
        return f"{self.namespace}/{self.name}/{self.system}".lower()

    def get_bucket_key(self, version: str) -> str:
        """Return bucket key."""
        return f"{self.module_id}/{version}/archive.tar.gz"

    def get_publish_url(self, bucket_name: str, version: str) -> str:
        """Return s3 url."""
        return ".".join(
            [
                f"s3::https://{bucket_name}",
                "s3",
                "/".join(["amazonaws.com", self.get_bucket_key(version=version)]),
            ]
        )
