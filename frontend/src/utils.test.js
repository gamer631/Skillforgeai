import { describe, expect, it } from 'vitest';
import { initialsForName } from './utils.js';

describe('initialsForName', () => {
  it('returns initials for first and last name', () => {
    expect(initialsForName('Krish Raut')).toBe('KR');
  });
  it('handles whitespace and a single name', () => {
    expect(initialsForName('  Anu   ')).toBe('A');
  });
  it('returns fallback for blank input', () => {
    expect(initialsForName('  ')).toBe('U');
  });
});
