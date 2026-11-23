'use client';

import {useEffect, useState} from 'react';
import {useTranslations} from 'next-intl';
import {getMarketDataProvider} from '@/lib/market';
import {useWatchlist} from '@/lib/watchlist';
import type {MarketAsset} from '@/types/market';

export default function WatchlistPage() {
  const t = useTranslations('Watchlist');
  const {ids, remove} = useWatchlist();
  const [assets, setAssets] = useState<MarketAsset[]>([]);

  useEffect(() => {
    const provider = getMarketDataProvider();
    Promise.all(ids.map((id) => provider.getAsset(id))).then((results) => {
      setAssets(results.filter((a): a is MarketAsset => a !== null));
    });
  }, [ids]);

  if (ids.length === 0) return <main className="p-6"><p>{t('empty')}</p></main>;

  return (
    <main className="min-h-screen p-6 space-y-4">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <ul className="space-y-2">
        {assets.map((a) => (
          <li key={a.id} className="border rounded p-3 flex justify-between">
            <a href={`/${window.location.pathname.split('/')[1]}/assets/${a.id}`} className="text-blue-600">{a.name}</a>
            <button onClick={() => remove(a.id)} className="text-red-600">{t('remove')}</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
