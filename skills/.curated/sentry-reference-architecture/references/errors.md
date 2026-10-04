# Error Handling Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `Cross-service traces broken` | Headers not propagated | Ensure trace headers included in service calls |
| `Too many projects` | Over-fragmentation | Consolidate projects by service domain |
| `Alert routing incorrect` | Missing team assignment | Associate projects with owning teams |
| `Inconsistent tagging` | No shared config | Use centralized SDK configuration package |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
