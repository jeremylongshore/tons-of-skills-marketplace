import { describe, expect, test } from 'vitest';
import { buildProgram } from './program.js';

describe('ccpi CLI program', () => {
  test('buildProgram registers expected commands', () => {
    const program = buildProgram();
    const commandNames = program.commands.map((cmd) => cmd.name());

    expect(program.name()).toBe('ccpi');
    expect(commandNames).toContain('install');
    expect(commandNames).toContain('upgrade');
    expect(commandNames).toContain('list');
    expect(commandNames).toContain('doctor');
    expect(commandNames).toContain('search');
    expect(commandNames).toContain('validate');
    expect(commandNames).toContain('analytics');
    expect(commandNames).toContain('marketplace');
    expect(commandNames).toContain('marketplace-add');
    expect(commandNames).toContain('marketplace-remove');
    expect(commandNames).toContain('skills');
  });
});
