import { describe, expect, test } from 'vitest';
import { buildProgram } from './program.js';

describe('ccpi CLI program', () => {
  test('buildProgram registers expected commands', () => {
    const program = buildProgram();
    const commandNames = program.commands.map((cmd) => cmd.name());
    const skills = program.commands.find((cmd) => cmd.name() === 'skills');

    expect(program.name()).toBe('ccpi');
    expect(commandNames).toEqual([
      'skills',
      'install',
      'upgrade',
      'list',
      'doctor',
      'search',
      'validate',
      'analytics',
      'marketplace',
      'marketplace-add',
      'marketplace-remove',
    ]);
    expect(skills?.commands.map((cmd) => cmd.name())).toEqual([
      'list-harnesses',
      'doctor',
      'install',
    ]);
    for (const command of skills?.commands ?? []) {
      expect(command).toHaveProperty('_actionHandler', expect.any(Function));
      expect(command.commands).toEqual([]);
    }
  });
});
