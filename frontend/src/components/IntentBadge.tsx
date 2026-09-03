import { INTENT_BADGE_COLORS } from '../constants';

interface IntentBadgeProps {
  intentValue: string;
}

export function IntentBadge({ intentValue }: IntentBadgeProps) {
  const color = INTENT_BADGE_COLORS[intentValue] ?? {
    bg: 'bg-gray-200',
    text: 'text-gray-700',
  };

  return (
    <span className={`mt-2 inline-block rounded-full px-2 py-1 text-xs ${color.bg} ${color.text}`}>
      {intentValue}
    </span>
  );
}