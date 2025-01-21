from aws_terraform_registry.common import TerraformModuleIdentifier


def test_tf_module_identifier():
    tf_id = TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")

    assert tf_id.module_id == "devops/kms/aws"


def test_tf_bucket_key():
    tf_id = TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")

    assert tf_id.get_bucket_key(version="1.0.0") == "devops/kms/aws/1.0.0/archive.tar.gz"


def test_tf_publish_url(mocker):
    mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="eu-west-1")
    tf_id = TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")
    assert (
        tf_id.get_publish_url(bucket_name="mybucket", version="1.0.0")
        == "s3::https://mybucket.s3-eu-west-1.amazonaws.com/devops/kms/aws/1.0.0/archive.tar.gz"
    )

    mocker.patch("aws_terraform_registry.common.model._find_caller_region", return_value="us-east-1")
    tf_id = TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")
    assert (
        tf_id.get_publish_url(bucket_name="mybucket", version="1.0.0")
        == "s3::https://mybucket.s3.amazonaws.com/devops/kms/aws/1.0.0/archive.tar.gz"
    )


def test_tf_blob_url(mocker):
    tf_id = TerraformModuleIdentifier(namespace="devops", name="kms", system="aws")
    assert (
        tf_id.get_blob_url(repository_url="https://registry.my-domain.con", version="1.0.0")
        == "https://registry.my-domain.con/blob/devops/kms/aws/1.0.0/archive.tar.gz"
    )
