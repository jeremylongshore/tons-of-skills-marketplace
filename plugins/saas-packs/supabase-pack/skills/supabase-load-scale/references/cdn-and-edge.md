# Compute Upgrades, CDN for Storage, and Edge Function Regions

## Compute Size Selection Guide

Use the project's current **Compute and Disk** settings and the [provider compute guide](https://supabase.com/docs/guides/platform/compute-and-disk) to review available sizes, CPU/RAM, connection budgets, storage performance, billing, and change impact. Record the selected configuration and observation date. Do not infer a current entitlement or connection guarantee from a fixed historical tier table.

Make approved compute changes in the Dashboard and validate the workload afterward; project listing is not a compute-change API.

## CDN Caching for Storage Buckets

Public buckets are automatically served through Supabase's CDN. Optimize cache behavior with proper headers and transforms.

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

// Upload with cache-control headers for CDN optimization
async function uploadPublicAsset(
  bucket: string,
  path: string,
  file: File
) {
  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(path, file, {
      cacheControl: '31536000',  // 1 year cache for immutable assets
      upsert: false,             // prevent accidental overwrites
      contentType: file.type,
    })

  if (error) throw new Error(`Upload failed: ${error.message}`)

  // Get the CDN-cached public URL
  const { data: { publicUrl } } = supabase.storage
    .from(bucket)
    .getPublicUrl(path, {
      transform: {
        width: 800,        // Image transforms are cached at the CDN edge
        quality: 80,
        format: 'webp',
      },
    })

  return { path: data.path, publicUrl }
}

// Bust cache by uploading to a new path (content-addressed)
import { createHash } from 'crypto'

async function uploadVersionedAsset(bucket: string, file: Buffer, ext: string) {
  const hash = createHash('sha256').update(file).digest('hex').slice(0, 12)
  const path = `assets/${hash}.${ext}`

  const { error } = await supabase.storage
    .from(bucket)
    .upload(path, file, {
      cacheControl: '31536000',
      upsert: false,
    })

  if (error && error.message !== 'The resource already exists') {
    throw new Error(`Versioned upload failed: ${error.message}`)
  }

  return supabase.storage.from(bucket).getPublicUrl(path).data.publicUrl
}
```

## Edge Function Regional Invocation

Deploy functions using the documented deployment workflow. Execution-region selection is an invocation option (`region` in the SDK or the documented request header), not a deployment flag. Measure latency relative to both users and the database; explicit region pinning also changes outage fallback behavior. Use the [regional invocation guide](https://supabase.com/docs/guides/functions/regional-invocation) for supported values and response metadata.

```typescript
// supabase/functions/geo-router/index.ts
// Application-level product filtering; not execution-region selection.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

Deno.serve(async (req) => {
  const reply = (status: number, body: unknown) => new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store' },
  })
  try {
    const authorization = req.headers.get('authorization')
    if (!authorization?.startsWith('Bearer ')) return reply(401, { error: 'Authentication required' })
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_PUBLISHABLE_KEY')!, {
        global: { headers: { Authorization: authorization } },
        auth: { persistSession: false, autoRefreshToken: false },
      }
    )
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) return reply(401, { error: 'User verification failed' })
    // Ordinary untrusted product filter: RLS authorizes rows, not this header.
    // It does not select the function's execution region.
    const { data, error } = await supabase.from('products').select('id, name, price')
      .eq('region', req.headers.get('x-region') ?? 'us').limit(20)
    if (error || !Array.isArray(data)) return reply(500, { error: 'Product query failed' })
    return reply(200, data)
  } catch {
    return reply(500, { error: 'Request failed' })
  }
})
```
