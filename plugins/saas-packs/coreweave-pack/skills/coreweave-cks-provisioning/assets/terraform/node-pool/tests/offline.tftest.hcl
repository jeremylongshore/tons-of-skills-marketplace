mock_provider "kubernetes" {}
variables {
  kubeconfig_path = "/nonexistent/offline-fixture"
  context         = "fixture"
  pool_name       = "fixture-pool"
  instance_type   = "fixture-instance"
  node_count      = 2
}
run "bounded_pool" {
  command = plan
  assert {
    condition     = kubernetes_manifest.operator_pool.manifest.spec.autoscaling == false
    error_message = "Fixture pool must not autoscale."
  }
  assert {
    condition     = kubernetes_manifest.operator_pool.manifest.spec.prefill.enabled == false
    error_message = "Fixture pool must not allocate replacement prefill capacity."
  }
}
