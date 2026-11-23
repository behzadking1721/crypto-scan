'use client';

import {useParams} from 'next/navigation';
import {useEffect, useRef, useState} from 'react';
import {useTranslations} from 'next-intl';
import {getMarketDataProvider} from '@/lib/market';
import WatchlistButton from '@/components/WatchlistButton';
import FreshnessBadge from '@/components/FreshnessBadge';
import type {MarketAsset, PriceHistoryRange, PriceHistoryResult} from '@/types/market';

const RANGES: PriceHistoryRange[] = ['1D', '7D', '30D', '90D', '1Y'];

export default function AssetDetailPage() {
  const params = useParams();
  const id = String(params?.id ?? '');
  const t = useTranslations('AssetDetail');
  const [asset, setAsset] = useState<MarketAsset | null>(null);
  const [history, setHistory] = useState<PriceHistoryResult | null>(null);
  const [range, setRange] = useState<PriceHistoryRange>('7D');
  const requestRef = useRef(0);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    const requestId = ++requestRef.current;
    const provider = getMarketDataProvider();
    setLoading(true);
    setNotFound(false);
    Promise.all([provider.getAsset(id), provider.getPriceHistory(id, range)])
      .then(([a, h]) => {
        if (requestId !== requestRef.current) return;
        if (!a) setNotFound(true);
        setAsset(a);
        setHistory(h);
      })
      .finally(() => {
        if (requestId === requestRef.current) setLoading(false);
      });
  }, [id, range]);

  if (loading) return <p>{t('loading')}</p>;
  if (notFound || !asset) return <p>{t('notFound')}</p>;

  return (
    <main className="min-h-screen p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{asset.name} ({asset.symbol})</h1>
        <div className="flex gap-2 items-center">
          <FreshnessBadge />
          <WatchlistButton assetId={asset.id} />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border p-4">
          <div className="text-sm text-gray-500">{t('price')}</div>
          <div className="text-xl font-semibold">${asset.priceUsd.toLocaleString()}</div>
        </div>
        <div className="rounded-xl border p-4">
          <div className="text-sm text-gray-500">{t('marketCap')}</div>
          <div className="text-xl font-semibold">${asset.marketCapUsd.toLocaleString()}</div>
        </div>
        <div className="rounded-xl border p-4">
          <div className="text-sm text-gray-500">{t('volume')}</div>
          <div className="text-xl font-semibold">${asset.volume24hUsd.toLocaleString()}</div>
        </div>
      </div>
      <div className="flex gap-2">
        {RANGES.map((r) => (
          <button key={r} onClick={() => setRange(r)} className={`px-3 py-1 border rounded ${range === r ? 'bg-blue-600 text-white' : ''}`}>{r}</button>
        ))}
      </div>
      <div className="rounded-xl border p-4">
        <div className="text-sm text-gray-500 mb-2">{t('history')} ({history?.isMock ? t('mock') : ''})</div>
        <svg viewBox="0 0 300 100" className="w-full h-40">
          {history && history.points.map((p, i) => {
            const x = (i / (history.points.length - 1)) * 300;
            const min = Math.min(...history.points.map((q) => q.priceUsd));
            const max = Math.max(...history.points.map((q) => q.priceUsd));
            const y = 100 - ((p.priceUsd - min) / (max - min || 1)) * 100;
            return <circle key={i} cx={x} cy={y} r="2" />;
          })}
        </svg>
      </div>
      <a href="../" className="text-blue-600">{t('back')}</a>
    </main>
  );
}
