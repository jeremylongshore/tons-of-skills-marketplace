# RDMA resource review

Check the communicating container, not a sidecar. CoreWeave documents `rdma/ib: 1`; Kubernetes defaults omitted requests from limits. A limit of 1 with no explicit request is valid for this review. A requests-only declaration, zero, or mismatched request/limit needs investigation. Inspect the admitted Pod if a LimitRange or admission controller changes defaults.

NCCL/OFED userspace, InfiniBand-capable Node Pool and effective network settings are separate prerequisites. Missing environment text in pasted YAML is not proof that MPI/operator-provided settings are absent. Do not install host drivers on managed Nodes.

Source checked 2026-11-05: [CoreWeave RDMA](https://docs.coreweave.com/products/networking/hpc-interconnect/use-gpudirect-rdma).
