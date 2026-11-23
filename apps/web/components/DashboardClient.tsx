'use client';

import {useEffect, useMemo, useState} from 'react';
import {useTranslations} from 'next-intl';
import WatchlistButton from '@/components/WatchlistButton';
import FreshnessBadge from '@/components/FreshnessBadge';
import {getMarketDataProvider} from '@/lib/market';
import type {MarketAsset, MarketOverview} from '@/types/market';

export default function DashboardClient() {
  const t = useTranslations('Dashboard');
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [assets, setAssets] = useState<MarketAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [sortBy, setSortBy] = useState<'marketCap' | 'price' | 'change24h' | 'volume'>('marketCap');

  useEffect(() => {
    const provider = getMarketDataProvider();
    setLoading(true);
    setError(null);
    Promise.all([provider.getOverview(), provider.listAssets({sortBy, sortDirection: 'desc'})])
      .then(([o, l]) => {
        setOverview(o);
        setAssets(l.items);
      })
      .catch((e) => setError(e instanceof Error ? e.message : 'Error'))
      .finally(() => setLoading(false));
  }, [sortBy]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return assets.filter((a) => a.name.toLowerCase().includes(q) || a.symbol.toLowerCase().includes(q));
  }, [assets, query]);

  if (loading) return <p>{t('loading')}</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <main className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <FreshnessBadge />
      </div>
      {overview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl border p-4">
            <div className="text-sm text-gray-500">{t('totalMarketCap')}</div>
            <div className="text-xl font-semibold">${overview.totalMarketCapUsd.toLocaleString()}</div>
          </div>
          <div className="rounded-xl border p-4">
            <div className="text-sm text-gray-500">{t('totalVolume')}</div>
            <div className="text-xl font-semibold">${overview.totalVolume24hUsd.toLocaleString()}</div>
          </div>
          <div className="rounded-xl border p-4">
            <div className="text-sm text-gray-500">{t('btcDominance')}</div>
            <div className="text-xl font-semibold">{overview.btcDominancePercent}%</div>
          </div>
        </div>
      )}
      <div className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t('search')}
          className="border rounded px-3 py-2 flex-1"
        />
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value as typeof sortBy)} className="border rounded px-3 py-2">
          <option value="marketCap">{t('marketCap')}</option>
          <option value="price">{t('price')}</option>
          <option value="change24h">{t('change24h')}</option>
          <option value="volume">{t('volume')}</option>
        </select>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b text-left">
              <th className="p-2">{t('asset')}</th>
              <th className="p-2">{t('price')}</th>
              <th className="p-2">{t('change24h')}</th>
              <th className="p-2">{t('marketCap')}</th>
              <th className="p-2">{t('watchlist')}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((a) => (
              <tr key={a.id} className="border-b">
                <td className="p-2">
                  <a href={`/assets/${a.id}`} className="font-medium text-blue-600">{a.name}</a>
                  <div className="text-xs text-gray-500">{a.symbol}</div>
                </td>
                <td className="p-2">${a.priceUsd.toLocaleString()}</td>
                <td className={`p-2 ${a.change24hPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {a.change24hPercent.toFixed(2)}%
                </td>
                <td className="p-2">${a.marketCapUsd.toLocaleString()}</td>
                <td className="p-2">${a.volume24hUsd.toLocaleString()}</td>
                <td className="p-2"><WatchlistButton assetId={a.id} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <p className="p-4 text-gray-500">{t('empty')}</p>}
      </div>
    </main>
  );
}
