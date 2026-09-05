# Host adapter rules

1. The portable `SKILL.md` remains complete when every adapter is deleted.
2. Adapters contain discovery, invocation, permission, model-routing, plugin,
   subagent, hook, or service-wiring details only.
3. Do not copy the skill body or references into per-host trees. Generate a thin
   adapter when a host requires another layout and add a drift check.
4. Capability absence fails closed by default. A documented degradation is
   allowed only when it preserves the outcome and safety boundary.
5. A support claim requires a current primary source and a fresh-environment
   discovery or invocation receipt. Source compatibility alone is not verified
   support.
6. Model names are adapter data. The portable workflow asks for an abstract
   class such as fast, balanced, or reasoning-high and accepts the host's choice.
7. Installation and uninstallation must be reversible and must not touch user
   state during tests; use disposable directories.

## Generic execution fallback

If a host has no native skill discovery, provide the complete `SKILL.md` and only
the referenced resources needed for the task as context. This proves manual
usability, not native installation or automatic activation.

If a host has no subagent facility, run role packets sequentially in the main
context. Label the final review as self-review unless a genuinely independent
identity reruns it.
