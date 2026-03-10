export const colors = {
  bg: '#09090b',
  card: '#18181b',
  cardHover: '#1f1f23',
  border: '#27272a',
  borderLight: '#3f3f46',
  surface: '#27272a',

  text: '#e4e4e7',
  textSecondary: '#a1a1aa',
  textMuted: '#71717a',
  textDim: '#52525b',
  white: '#ffffff',

  primary: '#6366f1',
  primaryDark: '#4f46e5',
  primaryGlow: 'rgba(99,102,241,0.15)',

  green: '#059669',
  greenDark: '#047857',
  greenLight: '#4ade80',
  greenBg: '#052e16',

  red: '#f87171',
  redBg: '#450a0a',

  yellow: '#facc15',
  yellowBg: '#422006',

  blue: '#60a5fa',
  blueBg: '#172554',

  // Story type badge colors
  badge: {
    book: { bg: '#1e3a5f', text: '#93c5fd' },
    movie: { bg: '#5f1e1e', text: '#fca5a5' },
    anime: { bg: '#1e5f3a', text: '#86efac' },
    show: { bg: '#5f4b1e', text: '#fcd34d' },
  } as Record<string, { bg: string; text: string }>,
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
} as const;

export const radius = {
  sm: 8,
  md: 10,
  lg: 12,
  xl: 16,
} as const;

export const fonts = {
  regular: { fontWeight: '400' as const },
  medium: { fontWeight: '500' as const },
  semibold: { fontWeight: '600' as const },
  bold: { fontWeight: '700' as const },
};

export const typeIcons: Record<string, string> = {
  book: '📖',
  movie: '🎬',
  anime: '🎌',
  show: '📺',
};
