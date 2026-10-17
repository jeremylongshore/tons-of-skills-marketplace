# Cohesivity services

Read a service's page with `get_cohesivity_documentation` (`{"document": "offering", "offering": "<name>"}`) before provisioning it. The same pages are at `https://cohesivity.ai/offerings/<name>`.

| Service | Name for `provision_resource` | What the app gets |
|---|---|---|
| Postgres | `postgres` | SQL over `https://cohesivity.ai/edge/postgres`, single queries or atomic batches |
| Redis | `redis` | Key-value storage and caching |
| Object storage | `object-storage` | File uploads and downloads |
| Vector database | `vector-database` | Embedding storage and similarity search |
| Hosting | `railway-hosting` | Deploys with a public URL |
| Workers | `cloudflare-workers` | A server tier for static sites |
| Login | `social-login` | Sign-in with Google |
| Realtime | `realtime` | Channels, presence and live updates |
| Email inbox | `inbox` | An address the app can send from and receive at |
| AI APIs | `openai-api`, `ai-gateway` | Model calls billed through the tenant |

The full, current list is in https://cohesivity.ai/llms.txt.
