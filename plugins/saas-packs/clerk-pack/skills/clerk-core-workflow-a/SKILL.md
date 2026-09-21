---
name: clerk-core-workflow-a
description: 'Implement user sign-up and sign-in flows with Clerk.

  Use when building authentication UI, customizing sign-in experience,

  or implementing OAuth social login.

  Trigger with phrases like "clerk sign-in", "clerk sign-up",

  "clerk login flow", "clerk OAuth", "clerk social login".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.15.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- clerk
- authentication
compatibility: Designed for Claude Code
---
# Clerk Core Workflow A: Sign-Up & Sign-In

## Overview

Implement authentication flows with Clerk: pre-built components for rapid setup, custom forms for full UI control, OAuth social login, email/phone verification, and multi-factor authentication.

## Prerequisites

- Clerk SDK installed and configured (`clerk-install-auth` completed)
- OAuth providers enabled in Dashboard > User & Authentication > Social Connections
- Sign-in/sign-up environment variables set

## Instructions

### Step 1: Pre-Built Components (Quick Start)

```typescript
// app/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignIn
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-xl rounded-2xl',
            headerTitle: 'text-2xl',
            socialButtonsBlockButton: 'rounded-lg',
          },
        }}
        routing="path"
        path="/sign-in"
        signUpUrl="/sign-up"
      />
    </div>
  )
}
```

```typescript
// app/sign-up/[[...sign-up]]/page.tsx
import { SignUp } from '@clerk/nextjs'

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" />
    </div>
  )
}
```

```bash
# .env.local — routing configuration
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding
```

### Step 2: Custom Sign-In Form (Full UI Control)

```typescript
'use client'
import { useSignIn } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export function CustomSignIn() {
  const { signIn, setActive, isLoaded } = useSignIn()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (!isLoaded) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await signIn.create({
        identifier: email,
        password,
      })

      if (result.status === 'complete') {
        // Session created — activate it and redirect
        await setActive({ session: result.createdSessionId })
        router.push('/dashboard')
      } else if (result.status === 'needs_second_factor') {
        // MFA required — handled in Step 5
        router.push('/sign-in/mfa')
      } else if (result.status === 'needs_identifier') {
        setError('Please enter your email address')
      }
    } catch (err: any) {
      const clerkError = err.errors?.[0]
      switch (clerkError?.code) {
        case 'form_identifier_not_found':
          setError('No account found with this email')
          break
        case 'form_password_incorrect':
          setError('Incorrect password')
          break
        case 'session_exists':
          router.push('/dashboard')
          break
        default:
          setError(clerkError?.message || 'Sign-in failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm mx-auto">
      <input
        type="email" value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email address" required
        className="w-full p-2 border rounded"
      />
      <input
        type="password" value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password" required
        className="w-full p-2 border rounded"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" disabled={loading} className="w-full p-2 bg-blue-600 text-white rounded">
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  )
}
```

### Step 3: OAuth Social Login

```typescript
'use client'
import { useSignIn } from '@clerk/nextjs'

export function OAuthButtons() {
  const { signIn, isLoaded } = useSignIn()

  if (!isLoaded) return null

  const signInWith = (strategy: 'oauth_google' | 'oauth_github' | 'oauth_apple') => {
    signIn.authenticateWithRedirect({
      strategy,
      redirectUrl: '/sso-callback',
      redirectUrlComplete: '/dashboard',
    })
  }

  return (
    <div className="flex flex-col gap-3">
      <button onClick={() => signInWith('oauth_google')} className="p-2 border rounded">
        Continue with Google
      </button>
      <button onClick={() => signInWith('oauth_github')} className="p-2 border rounded">
        Continue with GitHub
      </button>
      <button onClick={() => signInWith('oauth_apple')} className="p-2 border rounded">
        Continue with Apple
      </button>
    </div>
  )
}
```

```typescript
// app/sso-callback/page.tsx — handles OAuth redirect
import { AuthenticateWithRedirectCallback } from '@clerk/nextjs'

export default function SSOCallback() {
  return <AuthenticateWithRedirectCallback />
}
```

### Step 4: Custom Sign-Up with Email Verification

```typescript
'use client'
import { useSignUp } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export function CustomSignUp() {
  const { signUp, setActive, isLoaded } = useSignUp()
  const router = useRouter()
  const [step, setStep] = useState<'form' | 'verify'>('form')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')

  if (!isLoaded) return null

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await signUp.create({ emailAddress: email, password })
      // Send verification email
      await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
      setStep('verify')
    } catch (err: any) {
      setError(err.errors?.[0]?.longMessage || 'Sign-up failed')
    }
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const result = await signUp.attemptEmailAddressVerification({ code })
      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
        router.push('/onboarding')
      }
    } catch (err: any) {
      setError(err.errors?.[0]?.longMessage || 'Verification failed')
    }
  }

  if (step === 'verify') {
    return (
      <form onSubmit={handleVerify} className="space-y-4">
        <p>Check your email for a verification code</p>
        <input
          value={code} onChange={e => setCode(e.target.value)}
          placeholder="Enter 6-digit code" required
        />
        {error && <p className="text-red-500">{error}</p>}
        <button type="submit">Verify Email</button>
      </form>
    )
  }

  return (
    <form onSubmit={handleSignUp} className="space-y-4">
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />
      {error && <p className="text-red-500">{error}</p>}
      <button type="submit">Create Account</button>
    </form>
  )
}
```

### Step 5: Multi-Factor Authentication (TOTP)

```typescript
'use client'
import { useSignIn } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export function MFAVerification() {
  const { signIn, setActive } = useSignIn()
  const router = useRouter()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')

  const handleMFA = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const result = await signIn!.attemptSecondFactor({
        strategy: 'totp',
        code,
      })
      if (result.status === 'complete') {
        await setActive!({ session: result.createdSessionId })
        router.push('/dashboard')
      }
    } catch (err: any) {
      setError(err.errors?.[0]?.message || 'Invalid code')
    }
  }

  return (
    <form onSubmit={handleMFA} className="space-y-4">
      <h2>Two-Factor Authentication</h2>
      <p>Enter the code from your authenticator app</p>
      <input
        value={code} onChange={e => setCode(e.target.value)}
        placeholder="6-digit TOTP code" maxLength={6} required
        inputMode="numeric" pattern="[0-9]*"
      />
      {error && <p className="text-red-500">{error}</p>}
      <button type="submit">Verify</button>
    </form>
  )
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `form_identifier_not_found` | Email not registered | Show sign-up link or check Clerk instance |
| `form_password_incorrect` | Wrong password | Display error, offer password reset link |
| `session_exists` | Already signed in | Redirect to dashboard |
| `verification_failed` | Wrong or expired code | Allow retry; offer "Resend code" button |
| `oauth_callback_error` | OAuth misconfigured | Check redirect URIs in Dashboard > Social Connections |
| `identifier_already_signed_in` | Multi-session not enabled | Enable multi-session or redirect to dashboard |

## Enterprise Considerations

- Customize component appearance with Clerk's `appearance` prop or custom CSS -- matches your design system without building from scratch
- For Enterprise SSO (SAML/OIDC), users authenticate through their IdP; the `<SignIn>` component handles the redirect automatically
- Phone number verification uses `phone_code` strategy instead of `email_code`
- Magic link sign-in uses `email_link` strategy for passwordless auth
- Track sign-up conversion rates by subscribing to `user.created` webhooks
- MFA enrollment is managed via `<UserProfile />` component or `user.createTOTP()` API

## Resources

- [Sign-In Component](https://clerk.com/docs/components/authentication/sign-in)
- [Custom Sign-In Flow](https://clerk.com/docs/custom-flows/email-password)
- [OAuth Configuration](https://clerk.com/docs/authentication/social-connections/overview)
- [MFA Guide](https://clerk.com/docs/authentication/configuration/sign-up-sign-in-options#multi-factor-authentication)

## Next Steps

Proceed to `clerk-core-workflow-b` for session management and middleware.

## Output

- Working Clerk auth integration for the target stack (components + middleware/routes as applicable)
- Documented env vars (`CLERK_*`) and session verification path
- Checklist of production-hardening steps completed or explicitly deferred

## Examples

### Add Clerk to a Next.js App Router app

```
User: Wire Clerk auth into my Next.js App Router app with protected /dashboard.
Skill: installs Clerk packages, adds middleware, wraps layout with ClerkProvider,
       protects /dashboard, documents CLERK_SECRET_KEY + NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.
```

### Diagnose a broken session redirect

```
User: Users bounce between /sign-in and /dashboard in a loop.
Skill: traces middleware matcher, publicRoutes, and afterSignInUrl; fixes redirect cycle.
```
