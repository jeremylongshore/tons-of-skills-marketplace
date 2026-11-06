output "cluster_id" { value = coreweave_cks_cluster.operator.id }
output "vpc_id" { value = coreweave_networking_vpc.operator.id }
# No kubeconfig, token or account payload is emitted.
