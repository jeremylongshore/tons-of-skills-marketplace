# Uizze

**UI design that stands out**

![Uizze](https://raw.githubusercontent.com/uizze/uizze/main/plugins/openai-directory/uizze/assets/uizze-logo.png)

Uizze gives coding agents a free anti-ui-slop Skill and optional full MCP access to live UI references and license-clear materials. Use the skill to inspect the product and design system, write a design contract, cover required states, and run a bounded finish gate. The MCP answers one concrete unresolved UI question with strong full-screen references and finds license-clear materials for a concrete role.

## Get started

Install this package from the Claude plugin directory when available. For local testing:

```bash
claude --plugin-dir ./plugins/claude-directory
```

Use `/mcp` to authenticate the Uizze connection.

## Try it

> Help me ground a new interface in Uizze real screens.

> Find strong full-screen UI references for this unresolved interface question.

> Run the bounded UI finish gate on my rendered interface.

## Skill and MCP

The free skill includes its playbooks and licensing notices. It works without an account or MCP connection. The optional paid MCP uses the same Uizze account and service as the ChatGPT plugin. Complete the host’s native OAuth connection when prompted.

The MCP exposes `find_ui_references` and `find_ui_materials`. The skill’s finish gate uses the agent’s local inspection and rendering capabilities. No hosted review tool is included.

[Uizze](https://uizze.com/ai-ui-slop) · [Setup](https://uizze.com/docs) · [Support](https://uizze.com/contact) · [Privacy](https://uizze.com/privacy) · [Terms](https://uizze.com/terms)

## License

The bundled skill declares Apache-2.0 and retains third-party notices, including the MIT notice for identified iOS material. Keep LICENSE, NOTICE, and MODIFICATIONS.md with the skill.
