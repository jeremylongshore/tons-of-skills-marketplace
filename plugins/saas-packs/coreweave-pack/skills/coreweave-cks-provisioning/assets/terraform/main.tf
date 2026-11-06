# Original community template. New, independently owned state only.
resource "coreweave_networking_vpc" "operator" {
  name          = var.name
  zone          = var.zone
  host_prefixes = [{ name = "operator-hosts", type = "PRIMARY", prefixes = [var.host_cidr] }]
  vpc_prefixes = [
    { name = "operator-pods", value = var.pod_cidr },
    { name = "operator-services", value = var.service_cidr },
    { name = "operator-internal-lb", value = var.internal_lb_cidr }
  ]
  lifecycle { prevent_destroy = true }
}
resource "coreweave_cks_cluster" "operator" {
  name                   = var.name
  zone                   = var.zone
  version                = var.kubernetes_minor
  vpc_id                 = coreweave_networking_vpc.operator.id
  pod_cidr_name          = "operator-pods"
  service_cidr_name      = "operator-services"
  internal_lb_cidr_names = ["operator-internal-lb"]
  public                 = false
  lifecycle { prevent_destroy = true }
}
