# Same-device row-remapper evidence

A `Pending: Yes` value is used only from the `Remapped Rows` section of `nvidia-smi -q` (older tools label it Row Remapper) or an explicit structured CLI flag. Do not confuse a pending field from another subsystem with a memory-remap event.

For the supported ECC family, a pending remap informs recovery planning. A reported remapping failure is a reason to escalate with driver/DCGM diagnostics and NVIDIA's field diagnostic, not independent proof that every architecture has irreparable hardware. RMA review applies only when that field diagnostic fails. Do not let a remap field override a PCIe bus failure or an unknown code. Split multiple GPU identities before correlation.

Source: https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/index.html
