/**
 * Theme Tests
 */

describe('Theme', () => {
  it('exports colors', () => {
    const { colors } = require('../src/theme');

    expect(colors.background).toBe('#0D0D0D');
    expect(colors.accent).toBe('#00D9FF');
    expect(colors.textPrimary).toBe('#FFFFFF');
    expect(colors.rhythm).toBeDefined();
    expect(colors.harmony).toBeDefined();
    expect(colors.timbre).toBeDefined();
    expect(colors.motion).toBeDefined();
  });

  it('exports spacing', () => {
    const { spacing } = require('../src/theme');

    expect(spacing.xs).toBe(4);
    expect(spacing.sm).toBe(8);
    expect(spacing.md).toBe(16);
    expect(spacing.lg).toBe(24);
    expect(spacing.xl).toBe(32);
  });

  it('exports borderRadius', () => {
    const { borderRadius } = require('../src/theme');

    expect(borderRadius.sm).toBe(4);
    expect(borderRadius.md).toBe(8);
    expect(borderRadius.lg).toBe(12);
    expect(borderRadius.round).toBe(9999);
  });

  it('exports typography', () => {
    const { typography } = require('../src/theme');

    expect(typography.h1).toBeDefined();
    expect(typography.h1.fontSize).toBe(28);
    expect(typography.body).toBeDefined();
    expect(typography.mono).toBeDefined();
  });

  it('exports shadows', () => {
    const { shadows } = require('../src/theme');

    expect(shadows.sm).toBeDefined();
    expect(shadows.md).toBeDefined();
    expect(shadows.lg).toBeDefined();
    expect(shadows.sm.shadowColor).toBe('#000');
  });

  it('exports complete theme object', () => {
    const { theme } = require('../src/theme');

    expect(theme.colors).toBeDefined();
    expect(theme.spacing).toBeDefined();
    expect(theme.borderRadius).toBeDefined();
    expect(theme.typography).toBeDefined();
    expect(theme.shadows).toBeDefined();
  });
});
