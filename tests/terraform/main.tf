

locals {

  a = {
    id      = "test"
    id_full = "test"
    normalized_context = {
      id = "test"
    }
    tags_as_list_of_maps = [{
      id = "test"
    }]
  }

  b = {
    id      = "test2"
    id_full = "test2"
    normalized_context = {
      id = "test2"
    }
    tags_as_list_of_maps = [{
      id = "test2"
    }]
  }

}

resource "random_string" "random" {
  length           = 16
  special          = true
  override_special = "/@£$"
}

module "label_example_compare" {
  source  = "cloudposse/label/null//examples/complete/module/compare"
  version = "0.25.0"
  a       = local.a
  b       = local.b
}

resource "random_password" "pw" {
  length  = 16
  special = true
}

output "result1" {
  value = module.label_example_compare.equal
}

output "result2" {
  value = local.a
}

output "vars" {
  value = var.test_variable
}

output "pass" {
  value     = random_password.pw
  sensitive = true
}
