'use client';

import {useEffect, useState} from 'react';
import {getMarketDataProvider} from '@/lib/market';
import {useTranslations} from 'next-intl';

export default function FreshnessBadge() {
  const t = useTranslations('Freshness');
  const [text, setText] = useState(t('loading'));
  useEffect(() => {
    getMarketDataProvider()
      .getFreshness()
      .then((f) => setText(`${f.source} · ${f.lastUpdated}${f.isStale ? ` (${t('stale')})` : ''}`))
      .catch(() => setText(t('unknown')));
  }, [t]);
  return <span className="text-xs text-gray-500">{text}</span>;
}
