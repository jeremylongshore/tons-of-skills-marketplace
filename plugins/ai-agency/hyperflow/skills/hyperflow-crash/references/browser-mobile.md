# Browser and mobile evidence

Use existing authorized browser and design tools for responsive layout, navigation, screenshots, and interaction checks. Inspect real device or simulator behavior for native changes. Count occupied resources and use the configured cap; do not take over a user's session or claim devices that are unavailable.

Record browser/device, viewport, route, and steps. A source review or generated screenshot is not evidence that a host, browser, or device workflow passed.

## Vercel React Native guidance

For React Native and Expo tasks, also apply [Vercel's React Native skill](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/SKILL.md), version 1.0.0. The upstream skill declares MIT licensing. This reference adapts its routing and links to the original detailed rules; it does not bundle the full upstream manual.

During planning, inspect the installed RN/Expo version, list and navigation libraries, animation stack, native dependencies, and existing design primitives. Add applicable acceptance checks to the task workflow. During smash and crash, load only the relevant rule, verify compatibility against the repository, and record actual evidence. Existing project requirements and measured behavior determine whether a dependency change is justified.

| Task concern | Guidance to examine | Upstream rule |
|---|---|---|
| Long or heterogeneous lists | Virtualization, stable item identity, memoized rows/callbacks, item types, image cost, expensive render work. Compare supported list options using the actual workload. | [List virtualization](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/list-performance-virtualize.md) |
| Animations and gestures | Prefer transform/opacity, derived animation values and appropriate gesture handling. Preserve accessible press behavior and reduced motion. | [Animation properties](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/animation-gpu-properties.md) |
| Navigation | Check native stacks/tabs, transitions and platform behavior before introducing a custom navigator. | [Native navigators](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/navigation-native-navigators.md) |
| Images and platform UI | Inspect the image pipeline, native menus/modals, safe areas, scroll insets and layout measurement. Use existing supported primitives. | [Skill UI rules](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules) |
| State and rendering | Bound subscriptions, keep callbacks stable, render text through Text, and avoid falsy conditional-rendering bugs. Check compiler/Reanimated compatibility. | [Text rendering](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/rendering-text-in-text-component.md) |
| Native configuration and monorepos | Check app-owned native dependencies, one compatible dependency version, font config plugins and design-system import boundaries. | [Native dependency ownership](https://github.com/vercel-labs/agent-skills/blob/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-native-skills/rules/monorepo-native-deps-in-app.md) |

Use an already-installed `vercel-react-native-skills` skill through the active harness when available. Otherwise retrieve the pinned index and relevant linked rules with an available read-only source tool. If source retrieval or device execution is unavailable, state that limit. Never claim the skill itself ran an emulator, profiler, accessibility check or native build.
