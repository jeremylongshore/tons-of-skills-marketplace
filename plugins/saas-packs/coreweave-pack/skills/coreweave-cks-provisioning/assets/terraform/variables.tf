variable "name" {
  type        = string
  description = "Owner-selected new cluster and VPC name."
  validation {
    condition     = length(var.name) > 0 && length(var.name) <= 30
    error_message = "Name must contain 1 through 30 characters."
  }
}
variable "zone" {
  type        = string
  description = "Owner-confirmed zone with capacity and allowed addressing."
}
variable "kubernetes_minor" {
  type        = string
  description = "Owner-confirmed supported CKS minor version; not a hardcoded release."
  validation {
    condition     = can(regex("^v1\\.[0-9]+$", var.kubernetes_minor))
    error_message = "Use a documented supported minor version such as v1.N."
  }
}
variable "host_cidr" {
  type        = string
  description = "Owner-approved non-overlapping IPv4 range; verify against the zone and existing networks."
  validation {
    condition     = can(cidrnetmask(var.host_cidr))
    error_message = "An IPv4 CIDR is required."
  }
}
variable "pod_cidr" {
  type        = string
  description = "Owner-approved non-overlapping IPv4 range; verify against the zone and existing networks."
  validation {
    condition     = can(cidrnetmask(var.pod_cidr))
    error_message = "An IPv4 CIDR is required."
  }
}
variable "service_cidr" {
  type        = string
  description = "Owner-approved non-overlapping IPv4 range; verify against the zone and existing networks."
  validation {
    condition     = can(cidrnetmask(var.service_cidr))
    error_message = "An IPv4 CIDR is required."
  }
}
variable "internal_lb_cidr" {
  type        = string
  description = "Owner-approved non-overlapping IPv4 range; verify against the zone and existing networks."
  validation {
    condition     = can(cidrnetmask(var.internal_lb_cidr))
    error_message = "An IPv4 CIDR is required."
  }
}
