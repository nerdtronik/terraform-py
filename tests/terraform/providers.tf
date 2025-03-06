terraform {
  required_version = ">=0.15.0"
  required_providers {

    random = {
      source  = "hashicorp/random"
      version = ">=3.7.1"
    }
  }
}

provider "random" {
  # Configuration options
}
