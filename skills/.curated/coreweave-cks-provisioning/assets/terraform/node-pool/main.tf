terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "2.38.0" }
  }
}
provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.context
}
variable "kubeconfig_path" {
  type        = string
  description = "Private approved kubeconfig file; do not commit its contents."
}
variable "context" { type = string }
variable "pool_name" { type = string }
variable "instance_type" {
  type        = string
  description = "Exact owner-approved non-rack instance type; confirm GPUs per node separately."
}
variable "node_count" {
  type = number
  validation {
    condition     = var.node_count > 0 && floor(var.node_count) == var.node_count
    error_message = "A positive explicit node count is required."
  }
}
resource "kubernetes_manifest" "operator_pool" {
  manifest = {
    apiVersion = "compute.coreweave.com/v1alpha1"
    kind       = "NodePool"
    metadata   = { name = var.pool_name }
    spec = {
      computeClass = "default"
      instanceType = var.instance_type
      targetNodes  = var.node_count
      autoscaling  = false
      prefill      = { enabled = false }
      lifecycle    = { scaleDownStrategy = "IdleOnly" }
    }
  }
  lifecycle { prevent_destroy = true }
}
