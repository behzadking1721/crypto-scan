'use client';

import { useTranslations } from 'next-intl';
import { HealthStatus } from '@/lib/api';

interface StatusCardProps {
  labelKey: string;
  status: HealthStatus;
  error?: string;
}

const statusColors: Record<HealthStatus, { dot: string; label: string }> = {
  healthy: { dot: 'bg-[var(--positive)]', label: 'text-[var(--positive)] border-[var(--positive)]' },
  degraded: { dot: 'bg-[#F5A623]', label: 'text-[#F5A623] border-[#F5A623]' },
  unhealthy: { dot: 'bg-[var(--negative)]', label: 'text-[var(--negative)] border-[var(--negative)]' },
  unknown: { dot: 'bg-[var(--text-secondary)]', label: 'text-[var(--text-secondary)] border-[var(--text-secondary)]' },
  checking: { dot: 'bg-[var(--info)]', label: 'text-[var(--info)] border-[var(--info)]' }
};

export function StatusCard({ labelKey, status, error }: StatusCardProps) {
  const t = useTranslations('Health');
  const colors = statusColors[status];

  return (
    <div className="bg-[var(--card)] border border-[var(--secondary)] rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className={`w-2 h-2 rounded-full ${colors.dot}`} />
        <span className="text-sm font-medium text-[var(--text)]">{t(labelKey)}</span>
      </div>
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-xs font-medium uppercase tracking-wider ${colors.label}`}>{t(status)}</span>
      </div>
      {error && (
        <div className="mt-2 text-xs text-[var(--text-secondary)] break-words">{error}</div>
      )}
    </div>
  );
}
