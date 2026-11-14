# Xid recommendation boundaries

The implementation table in `scripts/triage.py` provides candidate next steps. It is not a hardware-health oracle. Read the current NVIDIA catalog for the actual GPU architecture and driver, then correlate DCGM and application evidence.

- 94: contained application memory event; restart the affected application according to supported recovery. NVIDIA also recommends a reset when convenient; do not declare the Node healthy or a reset never useful.
- 95: uncontained scope; supported devices require GPU recovery before affected applications restart. Coordinate managed recovery and checkpoint integrity.
- 13/31/43: investigate application, driver and preceding errors without categorically excluding hardware.
- 45: a follow-on (preemptive cleanup) code. Act on the accompanying Xid; it never governs when another code is present. Alone, NVIDIA's action is restarting Fabric Manager on NVSwitch systems.
- 48/63: correlate ECC/retirement/remap state with the same GPU.
- 64: reset the GPU or reboot the node, then contact support if it recurs. Not an RMA on its own.
- Remapping failure: take the GPU out of service and open a support case. RMA review applies only when NVIDIA's field diagnostic then fails.
- 74/79/119/120: collect topology/PCIe/GSP and driver diagnostics; disruptive recovery belongs to the lifecycle owner.
- 154: the driver's recovery action (`to 0xN (GPU Reset Required | Node Reboot Required | Drain and Reset | Drain P2P)`) sets the verdict and governs co-occurring codes.
- Unknown codes: investigate, with low confidence; no default reset. They rank below every mapped code, so they never override one.

Source checked 2026-11-05: [NVIDIA catalog](https://docs.nvidia.com/deploy/xid-errors/latest/analyzing-xid-catalog.html).
