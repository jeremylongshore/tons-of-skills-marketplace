mock_provider "coreweave" {}
variables {
  name             = "fixture-operator"
  zone             = "FIXTURE-ZONE"
  kubernetes_minor = "v1.33"
  host_cidr        = "10.0.0.0/20"
  pod_cidr         = "10.16.0.0/16"
  service_cidr     = "10.32.0.0/22"
  internal_lb_cidr = "10.48.0.0/22"
}
run "private_owned_cluster" {
  command = plan
  assert {
    condition     = coreweave_cks_cluster.operator.public == false
    error_message = "Fixture plan must not enable public cluster access."
  }
  assert {
    condition     = length(coreweave_networking_vpc.operator.vpc_prefixes) == 3
    error_message = "Pod, service and internal load-balancer ranges must be explicit."
  }
}
