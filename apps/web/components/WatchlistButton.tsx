'use client';

import {useWatchlist} from '@/lib/watchlist';
import {useTranslations} from 'next-intl';

export default function WatchlistButton({assetId}: {assetId: string}) {
  const t = useTranslations('Watchlist');
  const {has, toggle} = useWatchlist();
  const active = has(assetId);
  return (
    <button onClick={() => toggle(assetId)} className="px-3 py-1 border rounded">
      {active ? t('remove') : t('add')}
    </button>
  );
}
