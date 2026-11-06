terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    coreweave = { source = "coreweave/coreweave", version = "0.26.0" }
  }
}
# Read COREWEAVE_API_TOKEN from the approved secret environment; never output it.
provider "coreweave" {}
