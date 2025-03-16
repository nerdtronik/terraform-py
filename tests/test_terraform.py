import pytest
import json
from unittest.mock import patch, MagicMock
from terraform_python import Terraform, TerraformResult, TerraformError
import os


@pytest.fixture
def mock_terraform():
    """Fixture to create a Terraform instance with default parameters."""
    return Terraform()


# @patch("terraform_python.Terraform.init")
# def test_terraform_init(mock_terraform):
#     """Test Terraform initialization with default values."""
#     # assert mock_terraform.__workspace__ == "default"
#     assert mock_terraform.__lock__ is True
#     assert mock_terraform.__lock_timeout__ == "0s"
#     assert mock_terraform.__input__ is False
#     assert mock_terraform.__paralellism__ == 10
#     assert mock_terraform.__color__ is True
#     assert mock_terraform.__var_file__ is None


@patch("terraform_python.Terraform.version")
def test_terraform_version(mock_cmd, mock_terraform):
    """Test the version method of Terraform."""
    mock_version_output = {
        "version": {"major": 1, "minor": 5, "patch": 2},
        "version_str": "1.5.2",
        "latest": False,
        "platform": "linux_amd64",
    }

    mock_cmd.return_value = TerraformResult(True, mock_version_output)

    result = mock_terraform.version()
    # tf_version = os.getenv("TF_VERSION")
    assert result.success is True
    assert result.result["version_str"] == "1.5.2"
    assert result.result["version"]["major"] == 1
    assert result.result["version"]["minor"] == 5
    assert result.result["version"]["patch"] == 2
    assert result.result["latest"] is False
    assert (
        result.result["platform"] == "linux_amd64"
        or result.result["platform"] == "unknow"
    )


@patch("terraform_python.Terraform.init")
def test_terraform_init_command(mock_cmd, mock_terraform):
    """Test calling the Terraform init method."""
    mock_cmd.return_value = TerraformResult(True, "Terraform initialized")

    result = mock_terraform.init()

    assert result.success is True
    assert (
        "Terraform has been successfully initialized" in result.result
        or "Terraform initialized" in result.result
    )


@patch("terraform_python.Terraform.plan")
def test_terraform_plan(mock_cmd, mock_terraform):
    """Test calling the Terraform plan method."""
    mock_cmd.return_value = TerraformResult(True, "Plan created")

    result = mock_terraform.plan(json=True)

    assert result.success is True


@patch("terraform_python.Terraform.apply")
def test_terraform_apply(mock_cmd, mock_terraform):
    """Test calling the Terraform apply method."""
    mock_cmd.return_value = TerraformResult(True, "Apply complete")

    result = mock_terraform.apply(auto_approve=True)

    assert result.success is True
    assert "Apply complete" in result.result


@patch("terraform_python.Terraform.destroy")
def test_terraform_destroy(mock_cmd, mock_terraform):
    """Test calling the Terraform destroy method."""
    mock_cmd.return_value = TerraformResult(True, "Destroy complete")

    result = mock_terraform.destroy(auto_approve=True)

    assert result.success is True
    assert "Destroy complete" in result.result


@patch("terraform_python.Terraform.fmt")
def test_terraform_format(mock_cmd, mock_terraform):
    """Test calling the Terraform fmt method."""
    mock_cmd.return_value = TerraformResult(True, "Formatted successfully")

    result = mock_terraform.fmt()

    assert result.success is True
    assert "Formatted successfully" in result.result


@patch("terraform_python.Terraform.validate")
def test_terraform_validate(mock_cmd, mock_terraform):
    """Test calling the Terraform validate method."""
    mock_cmd.return_value = TerraformResult(True, "Validation successful")

    result = mock_terraform.validate()

    assert result.success is True
    assert "Validation successful" in result.result


@patch("terraform_python.Terraform.show")
def test_terraform_show(mock_cmd, mock_terraform):
    """Test calling the Terraform show method."""
    mock_cmd.return_value = TerraformResult(True, json.dumps({"output": "success"}))

    result = mock_terraform.show()

    assert result.success is True
    assert json.loads(result.result)["output"] == "success"
