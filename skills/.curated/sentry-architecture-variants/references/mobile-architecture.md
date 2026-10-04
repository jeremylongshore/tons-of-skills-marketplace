# Mobile Architecture (React Native) — Sentry Deep Dive

## Setup with @sentry/react-native

```typescript
// App.tsx — initialize before any other code
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: __DEV__ ? 'development' : 'production',
  tracesSampleRate: 0.2,

  integrations: [
    Sentry.reactNativeTracingIntegration({
      routingInstrumentation:
        Sentry.reactNavigationIntegration(),  // React Navigation
    }),
  ],

  // Connect mobile traces to backend API
  tracePropagationTargets: [
    /^https:\/\/api\.yourapp\.com/,
  ],

  // Capture native crashes (iOS + Android)
  enableNativeCrashHandling: true,
  enableAutoSessionTracking: true,
  attachScreenshot: true,                // attach screenshot on crash
  attachViewHierarchy: true,             // attach view tree on crash
});

// Wrap root component
export default Sentry.wrap(App);
```

## Source Maps and Debug Symbols

Upload source maps and dSYMs in CI for readable stack traces:

```bash
# JavaScript source maps
npx sentry-cli sourcemaps upload \
  --release 1.0.0 \
  --dist 1 \
  ./dist

# iOS dSYMs
npx sentry-cli upload-dif \
  --include-sources \
  ./ios/build/Build/Products/Release-iphoneos

# Android ProGuard/R8 mappings
npx sentry-cli upload-dif \
  ./android/app/build/outputs/mapping/release/mapping.txt
```

## Navigation Instrumentation

Track screen transitions as spans:

```typescript
import { NavigationContainer } from '@react-navigation/native';
import * as Sentry from '@sentry/react-native';

const routingIntegration = Sentry.reactNavigationIntegration();

function App() {
  const navigation = React.useRef(null);

  return (
    <NavigationContainer
      ref={navigation}
      onReady={() => routingIntegration.registerNavigationContainer(navigation)}
    >
      {/* screens */}
    </NavigationContainer>
  );
}
```

## Native Crash Reporting

Sentry React Native captures both JavaScript and native crashes:

- **JavaScript errors**: Caught by the JS error handler, sent with full JS stack trace
- **iOS crashes**: Native crash handler captures Mach exceptions and POSIX signals
- **Android crashes**: Native crash handler captures JVM and NDK crashes
- **ANR detection**: Automatic detection of Application Not Responding events

All crash types are unified in the same Sentry project with proper symbolication when source maps/dSYMs are uploaded.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
