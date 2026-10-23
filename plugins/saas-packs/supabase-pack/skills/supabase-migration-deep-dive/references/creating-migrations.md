# Creating and Managing Migrations

Use the Supabase CLI to create, test, and apply migrations. Each migration is a timestamped SQL file that runs in order.

**Create a new migration:**

```bash
# Create a migration file with a descriptive name
npx supabase migration new add_profiles_table
# Creates: supabase/migrations/20260322120000_add_profiles_table.sql

# List all migrations and their status
npx supabase migration list

# Inspect local migration history without resetting data
npx supabase migration list --local
```

`db reset` is destructive and has no dry-run option. Review migration files and history first; test a reset only against an approved disposable local database. `db diff` compares schemas and is not a reset preview.

**Write the migration SQL:**

```sql
-- supabase/migrations/20260322120000_add_profiles_table.sql

-- Create the profiles table
CREATE TABLE public.profiles (
  id uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email text UNIQUE NOT NULL,
  full_name text,
  avatar_url text,
  bio text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "users_read_own_profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_update_own_profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Create an index for email lookups
CREATE INDEX idx_profiles_email ON public.profiles(email);

-- Auto-create profile on user signup (trigger)
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    new.id,
    new.email,
    new.raw_user_meta_data ->> 'full_name',
    new.raw_user_meta_data ->> 'avatar_url'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated_at trigger
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS trigger AS $$
BEGIN
  new.updated_at = now();
  RETURN new;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
```

**Test the migration locally:**

```bash
# Apply all migrations and seed data (destructive — resets local DB)
npx supabase db reset

# Run pgTAP tests if configured
npx supabase test db

# Verify the schema
npx supabase db lint

# Generate updated TypeScript types
npx supabase gen types typescript --local > lib/database.types.ts
```

**Apply migrations to remote environments:**

```text
# Push to staging
npx supabase link --project-ref <staging-ref>
npx supabase db push
# Verify: npx supabase migration list --linked

# Push to production (same migration files)
npx supabase link --project-ref <prod-ref>
npx supabase db push
```
