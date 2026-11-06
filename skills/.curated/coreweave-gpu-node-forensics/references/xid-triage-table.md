# Xid recommendation boundaries

The implementation table in `scripts/triage.py` provides candidate next steps. It is not a hardware-health oracle. Read the current NVIDIA catalog for the actual GPU architecture and driver, then correlate DCGM and application evidence.

- 94: contained application memory event; restart the affected application according to supported recovery. NVIDIA also recommends a reset when convenient; do not declare the Node healthy or a reset never useful.
- 95: uncontained scope; supported devices require GPU recovery before affected applications restart. Coordinate managed recovery and checkpoint integrity.
- 13/31/43/45: investigate application, driver and preceding errors without categorically excluding hardware.
- 48/63/64: correlate ECC/retirement/remap state with the same GPU. Replacement requires supported diagnostics and platform review.
- 74/79/119/120: collect topology/PCIe/GSP and driver diagnostics; disruptive recovery belongs to the lifecycle owner.
- Unknown codes: investigate, with low confidence; no default reset.

Source checked 2026-11-05: [NVIDIA catalog](https://docs.nvidia.com/deploy/xid-errors/latest/analyzing-xid-catalog.html).
