/**
 * Single source of truth for the marketplace response-security policy.
 *
 * The site is static, so production headers come from Caddy while local
 * development and the dependency-free static preview use this module directly.
 * Keeping the values here prevents those enforcement layers from drifting.
 */

import { posix } from 'node:path';

// script-src has no inline exception: the built site ships no executable
// inline script or event handler (bead claude-i076; enforced by the empty
// marketplace/ops/csp-inline-inventory.json gate), and validateSecurityPolicy
// rejects 'unsafe-inline' in script-src outright.
export const CSP_INLINE_JUSTIFICATIONS = Object.freeze({
  'style-src':
    'Astro component styles and a small number of generated style attributes are inline in the static output.',
});

export const CSP_DIRECTIVES = Object.freeze({
  'default-src': ["'self'"],
  'base-uri': ["'self'"],
  'object-src': ["'none'"],
  'frame-ancestors': ["'self'"],
  'form-action': ["'self'"],
  'script-src': [
    "'self'",
    'https://analytics.intentsolutions.io',
    'https://www.googletagmanager.com',
    'https://cdn.jsdelivr.net',
    'https://gettermscdn.com',
  ],
  'style-src': ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
  'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com'],
  'img-src': [
    "'self'",
    'data:',
    'https://github.com',
    'https://avatars.githubusercontent.com',
    'https://www.google-analytics.com',
    'https://www.googletagmanager.com',
  ],
  'connect-src': [
    "'self'",
    'https://analytics.intentsolutions.io',
    'https://www.google-analytics.com',
    'https://analytics.google.com',
    'https://region1.google-analytics.com',
    'https://stats.g.doubleclick.net',
    'https://gettermscdn.com',
  ],
  'frame-src': ["'self'", 'https://gettermscdn.com'],
  'media-src': ["'self'"],
  'manifest-src': ["'self'"],
  'worker-src': ["'self'", 'blob:'],
});

export const CHAT_CSP_DIRECTIVES = Object.freeze({
  ...CSP_DIRECTIVES,
  // Deliberate route-scoped exception: /chats accepts user-supplied WebSocket
  // endpoints, so hosts cannot be enumerated. `ws:` supports local HTTP
  // preview; browsers still block mixed-content ws:// in production.
  'connect-src': [...CSP_DIRECTIVES['connect-src'], 'wss:', 'ws:'],
});

export function serializeCsp(directives = CSP_DIRECTIVES) {
  return Object.entries(directives)
    .map(([name, values]) => [name, ...values].join(' '))
    .join('; ');
}

export function validateSecurityPolicy(
  directives = CSP_DIRECTIVES,
  inlineJustifications = CSP_INLINE_JUSTIFICATIONS,
  reviewedDirectives = CSP_DIRECTIVES,
  { allowWebSocketSchemes = false } = {},
) {
  const required = {
    'default-src': "'self'",
    'base-uri': "'self'",
    'object-src': "'none'",
    'frame-ancestors': "'self'",
    'form-action': "'self'",
  };
  for (const [name, requiredValue] of Object.entries(required)) {
    if (directives[name]?.length !== 1 || directives[name][0] !== requiredValue) {
      throw new Error(`${name} must be the reviewed singleton ${requiredValue}`);
    }
  }

  if (Object.hasOwn(directives, 'upgrade-insecure-requests')) {
    throw new Error(
      'upgrade-insecure-requests is forbidden because the reviewed local-preview contract uses HTTP',
    );
  }

  const reviewedNames = Object.keys(reviewedDirectives);
  if (
    Object.keys(directives).length !== reviewedNames.length ||
    reviewedNames.some((name) => !Object.hasOwn(directives, name))
  ) {
    throw new Error('CSP directives must match the reviewed directive allowlist');
  }

  for (const [name, values] of Object.entries(directives)) {
    if (values.includes('*')) throw new Error(`${name} may not contain a wildcard source`);
    if (values.includes("'unsafe-eval'")) throw new Error(`${name} may not allow unsafe-eval`);
    if (['script-src', 'default-src'].includes(name) && values.includes("'unsafe-inline'")) {
      throw new Error(`${name} may not allow unsafe-inline; the site ships no inline script`);
    }
    for (const value of values) {
      if (/^https?:$/u.test(value)) {
        throw new Error(`${name} may not contain the broad scheme-only source ${value}`);
      }
      if (/^wss?:$/u.test(value) && (!allowWebSocketSchemes || name !== 'connect-src')) {
        throw new Error(`${name} may not contain the unreviewed WebSocket source ${value}`);
      }
    }
    if (values.includes("'unsafe-inline'") && !inlineJustifications[name]) {
      throw new Error(`${name} unsafe-inline requires an explicit justification`);
    }
    const reviewedValues = reviewedDirectives[name];
    if (
      values.length !== reviewedValues.length ||
      values.some((value, index) => value !== reviewedValues[index])
    ) {
      throw new Error(`${name} must match the reviewed source allowlist`);
    }
  }
  return true;
}

validateSecurityPolicy();
validateSecurityPolicy(CHAT_CSP_DIRECTIVES, CSP_INLINE_JUSTIFICATIONS, CHAT_CSP_DIRECTIVES, {
  allowWebSocketSchemes: true,
});

export const MARKETPLACE_SECURITY_HEADERS = Object.freeze({
  'Content-Security-Policy': serializeCsp(),
  'Permissions-Policy':
    'accelerometer=(), autoplay=(), camera=(), display-capture=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
});

export const MARKETPLACE_CHAT_SECURITY_HEADERS = Object.freeze({
  ...MARKETPLACE_SECURITY_HEADERS,
  'Content-Security-Policy': serializeCsp(CHAT_CSP_DIRECTIVES),
});

export function normalizeRequestPath(requestTarget) {
  if (
    typeof requestTarget !== 'string' ||
    !requestTarget.startsWith('/') ||
    requestTarget.startsWith('//')
  ) {
    return null;
  }

  const rawPath = requestTarget.split(/[?#]/u, 1)[0];
  let normalizedPath;
  try {
    normalizedPath = decodeURIComponent(rawPath);
  } catch {
    return null;
  }
  if (
    !normalizedPath.startsWith('/') ||
    normalizedPath.startsWith('//') ||
    normalizedPath.includes('\0') ||
    normalizedPath.includes('\\')
  ) {
    return null;
  }
  return posix.normalize(normalizedPath);
}

export function securityHeadersForPath(requestTarget) {
  const normalizedPath = normalizeRequestPath(requestTarget);
  return normalizedPath !== null &&
    (normalizedPath === '/chats' || normalizedPath.startsWith('/chats/'))
    ? MARKETPLACE_CHAT_SECURITY_HEADERS
    : MARKETPLACE_SECURITY_HEADERS;
}
