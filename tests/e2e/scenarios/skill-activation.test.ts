import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import path from 'path';
import fs from 'fs/promises';
import {
  createTestEnv,
  installPlugin,
  loadSkill,
  activateSkill,
  type TestEnvironment,
  type Skill
} from '../setup';

describe('Skill Activation', () => {
  let env: TestEnvironment;

  beforeEach(async () => {
    env = await createTestEnv();
  });

  afterEach(async () => {
    await env.cleanup();
  });

  describe('Skill Loading', () => {
    it('should load skill from installed plugin', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill).toBeDefined();
      expect(skill.name).toBe('test-skill');
      expect(skill.version).toBe('1.0.0');
      expect(skill.license).toBe('MIT');
    });

    it('should parse skill frontmatter correctly', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.name).toBe('test-skill');
      expect(skill.description).toContain('Test skill for E2E validation');
      expect(skill.author).toContain('Test Author');
      expect(skill.version).toBe('1.0.0');
    });

    it('should parse folded CRLF descriptions and YAML-list tools', async () => {
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);
      const skillPath = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'yaml-shapes'
      );
      await fs.mkdir(skillPath, { recursive: true });
      await fs.writeFile(
        path.join(skillPath, 'SKILL.md'),
        [
          '---',
          'name: yaml-shapes',
          'description: >-',
          '  Trigger with "folded trigger" across',
          '  multiple source lines.',
          'allowed-tools:',
          '  - Read',
          '  - Bash(git status)',
          'version: 1.0.0',
          'author: Test',
          'license: MIT',
          'compatibility: Test harness',
          'tags: [testing, yaml]',
          '---',
          '# YAML shapes'
        ].join('\r\n')
      );

      const skill = await loadSkill(env, 'test-plugin', 'yaml-shapes');

      expect(skill.description).toBe(
        'Trigger with "folded trigger" across multiple source lines.'
      );
      expect(skill.allowedTools).toEqual(['Read', 'Bash(git status)']);
      expect(skill.triggerPhrases).toContain('folded trigger');
    });

    it('should fail closed on malformed and non-mapping YAML', async () => {
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      for (const [name, frontmatter] of [
        ['duplicate-key', 'name: first\nname: second'],
        ['non-mapping', '- name\n- description'],
        ['unsafe-key', '__proto__: polluted\nname: unsafe']
      ]) {
        const skillPath = path.join(
          env.pluginsPath,
          'test-plugin',
          'skills',
          name
        );
        await fs.mkdir(skillPath, { recursive: true });
        await fs.writeFile(
          path.join(skillPath, 'SKILL.md'),
          `---\n${frontmatter}\n---\n# Invalid`
        );

        await expect(loadSkill(env, 'test-plugin', name)).rejects.toThrow();
      }
      expect(Object.prototype).not.toHaveProperty('polluted');
    });

    it('should extract allowed-tools from frontmatter', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.allowedTools).toBeInstanceOf(Array);
      expect(skill.allowedTools).toContain('Read');
      expect(skill.allowedTools).toContain('Write');
      expect(skill.allowedTools).toContain('Bash(pnpm:*)');
    });

    it('should reject skill with invalid frontmatter', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Create skill with invalid frontmatter
      const invalidSkillPath = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'invalid-skill'
      );
      await fs.mkdir(invalidSkillPath, { recursive: true });
      await fs.writeFile(
        path.join(invalidSkillPath, 'SKILL.md'),
        'No frontmatter here'
      );

      // Act & Assert
      await expect(loadSkill(env, 'test-plugin', 'invalid-skill'))
        .rejects
        .toThrow('Invalid skill: missing frontmatter');
    });

    it('should reject loading skill from non-existent plugin', async () => {
      // Act & Assert
      await expect(loadSkill(env, 'non-existent', 'test-skill'))
        .rejects
        .toThrow('Plugin non-existent is not installed');
    });
  });

  describe('Trigger Phrase Detection', () => {
    it('should detect trigger phrase in user input', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await activateSkill(env, 'run test skill');

      // Assert
      expect(skill).toBeDefined();
      expect(skill?.name).toBe('test-skill');
    });

    it('should match trigger phrases case-insensitively', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill1 = await activateSkill(env, 'RUN TEST SKILL');
      const skill2 = await activateSkill(env, 'run test skill');
      const skill3 = await activateSkill(env, 'Run Test Skill');

      // Assert
      expect(skill1?.name).toBe('test-skill');
      expect(skill2?.name).toBe('test-skill');
      expect(skill3?.name).toBe('test-skill');
    });

    it('should match trigger phrases in context', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act - trigger phrase embedded in longer sentence
      const skill = await activateSkill(
        env,
        'I need to run test skill for validation'
      );

      // Assert
      expect(skill).toBeDefined();
      expect(skill?.name).toBe('test-skill');
    });

    it('should return null when no trigger phrase matches', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await activateSkill(env, 'completely unrelated input');

      // Assert
      expect(skill).toBeNull();
    });

    it('should extract multiple trigger phrases from description', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.triggerPhrases.length).toBeGreaterThan(0);
      expect(skill.triggerPhrases).toContain('run test skill');
      expect(skill.triggerPhrases).toContain('execute test');
    });
  });

  describe('Tool Permissions', () => {
    it('should validate allowed-tools format', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.allowedTools).toBeInstanceOf(Array);
      expect(skill.allowedTools.length).toBeGreaterThan(0);

      // Each tool should be a non-empty string
      for (const tool of skill.allowedTools) {
        expect(typeof tool).toBe('string');
        expect(tool.length).toBeGreaterThan(0);
      }
    });

    it('should parse basic tool permissions', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert - verify common tools
      const basicTools = ['Read', 'Write', 'Edit', 'Grep'];
      const hasBasicTool = skill.allowedTools.some(tool =>
        basicTools.includes(tool) || tool.startsWith('Bash(')
      );
      expect(hasBasicTool).toBe(true);
    });

    it('should handle restricted tool permissions', async () => {
      // Arrange - create skill with restricted tools
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      const restrictedSkillPath = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'restricted-skill'
      );
      await fs.mkdir(restrictedSkillPath, { recursive: true });
      await fs.writeFile(
        path.join(restrictedSkillPath, 'SKILL.md'),
        `---
name: restricted-skill
description: Skill with restricted tools
allowed-tools: Bash(diff:*), Bash(grep:*)
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Restricted skill content`
      );

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'restricted-skill');

      // Assert
      expect(skill.allowedTools).toContain('Bash(diff:*)');
      expect(skill.allowedTools).toContain('Bash(grep:*)');
    });

    it('should handle read-only tool permissions', async () => {
      // Arrange - create skill with read-only tools
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      const readOnlySkillPath = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'readonly-skill'
      );
      await fs.mkdir(readOnlySkillPath, { recursive: true });
      await fs.writeFile(
        path.join(readOnlySkillPath, 'SKILL.md'),
        `---
name: readonly-skill
description: Read-only skill
allowed-tools: Read, Grep
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Read-only skill content`
      );

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'readonly-skill');

      // Assert
      expect(skill.allowedTools).toEqual(['Read', 'Grep']);
      expect(skill.allowedTools).not.toContain('Write');
      expect(skill.allowedTools).not.toContain('Edit');
    });

    it('should preserve scoped tools in canonical space-separated form', async () => {
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);
      const skillPath = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'scoped-skill'
      );
      await fs.mkdir(skillPath, { recursive: true });
      await fs.writeFile(
        path.join(skillPath, 'SKILL.md'),
        `---
name: scoped-skill
description: Trigger with "scoped skill"
allowed-tools: Read Bash(git status) Bash(git diff *)
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Scoped skill content`
      );

      const skill = await loadSkill(env, 'test-plugin', 'scoped-skill');

      expect(skill.allowedTools).toEqual([
        'Read',
        'Bash(git status)',
        'Bash(git diff *)'
      ]);
    });
  });

  describe('Multiple Skills', () => {
    it('should load multiple skills from same plugin', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Create second skill
      const skill2Path = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'test-skill-2'
      );
      await fs.mkdir(skill2Path, { recursive: true });
      await fs.writeFile(
        path.join(skill2Path, 'SKILL.md'),
        `---
name: test-skill-2
description: Second test skill with "alternate trigger"
allowed-tools: Read
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Second skill content`
      );

      // Act
      const skill1 = await loadSkill(env, 'test-plugin', 'test-skill');
      const skill2 = await loadSkill(env, 'test-plugin', 'test-skill-2');

      // Assert
      expect(skill1.name).toBe('test-skill');
      expect(skill2.name).toBe('test-skill-2');
      expect(skill1.name).not.toBe(skill2.name);
    });

    it('should activate correct skill based on trigger phrase', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Create second skill with different trigger
      const skill2Path = path.join(
        env.pluginsPath,
        'test-plugin',
        'skills',
        'test-skill-2'
      );
      await fs.mkdir(skill2Path, { recursive: true });
      await fs.writeFile(
        path.join(skill2Path, 'SKILL.md'),
        `---
name: test-skill-2
description: Trigger with "alternate trigger" phrase
allowed-tools: Read
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Second skill content`
      );

      // Act
      const skill1 = await activateSkill(env, 'run test skill');
      const skill2 = await activateSkill(env, 'alternate trigger');

      // Assert
      expect(skill1?.name).toBe('test-skill');
      expect(skill2?.name).toBe('test-skill-2');
    });

    it('should search skills across multiple plugins', async () => {
      // Arrange - install first plugin
      const plugin1Path = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, plugin1Path);

      // Create and install second plugin
      const plugin2Path = path.join(env.basePath, 'test-plugin-2');
      await fs.mkdir(path.join(plugin2Path, '.claude-plugin'), { recursive: true });
      await fs.writeFile(
        path.join(plugin2Path, '.claude-plugin', 'plugin.json'),
        JSON.stringify({
          name: 'test-plugin-2',
          version: '1.0.0',
          description: 'Second test plugin',
          author: { name: 'Test', email: 'test@example.com' },
          license: 'MIT'
        })
      );
      await fs.writeFile(path.join(plugin2Path, 'README.md'), '# Plugin 2');

      const skill2Path = path.join(plugin2Path, 'skills', 'plugin2-skill');
      await fs.mkdir(skill2Path, { recursive: true });
      await fs.writeFile(
        path.join(skill2Path, 'SKILL.md'),
        `---
name: plugin2-skill
description: Skill from plugin 2 with "second plugin trigger"
allowed-tools: Read
version: 1.0.0
license: MIT
author: Test
compatibility: Test harness
tags: [testing]
---

Plugin 2 skill content`
      );

      await installPlugin(env, plugin2Path);

      // Act
      const skill1 = await activateSkill(env, 'run test skill');
      const skill2 = await activateSkill(env, 'second plugin trigger');

      // Assert
      expect(skill1?.name).toBe('test-skill');
      expect(skill2?.name).toBe('plugin2-skill');
    });
  });

  describe('Skill Content', () => {
    it('should include full skill content', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.content).toBeTruthy();
      expect(skill.content).toContain('---'); // Frontmatter
      expect(skill.content).toContain('test-skill'); // Skill name
    });

    it('should preserve skill instructions', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.content).toContain('SKILL.md'); // Should preserve content
      expect(skill.content.length).toBeGreaterThan(100); // Has substantial content
    });
  });

  describe('Current Marketplace Schema Compliance', () => {
    it('should require allowed-tools field', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.allowedTools).toBeDefined();
      expect(skill.allowedTools.length).toBeGreaterThan(0);
    });

    it('should require version field', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.version).toBeDefined();
      expect(skill.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it('should include trigger phrases in description', async () => {
      // Arrange
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      // Act
      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      // Assert
      expect(skill.description).toBeTruthy();
      expect(skill.triggerPhrases.length).toBeGreaterThan(0);
    });

    it('should require compatibility and tags', async () => {
      const pluginPath = path.join(__dirname, '../fixtures/test-plugin');
      await installPlugin(env, pluginPath);

      const skill = await loadSkill(env, 'test-plugin', 'test-skill');

      expect(skill.compatibility).toContain('model-agnostic');
      expect(skill.tags).toEqual(['testing', 'e2e']);
    });
  });
});
