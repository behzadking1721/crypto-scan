import type { MarketAsset, MarketListResult, MarketOverview, MarketQuery, MarketFreshness, MarketDataProvider, PriceHistoryRange, PriceHistoryResult, PriceHistoryPoint } from '../../types/market';

const ASSETS: MarketAsset[] = [
  { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', priceUsd: 64000, change24hUsd: 1200, change24hPercent: 1.9, marketCapUsd: 1260000000000, volume24hUsd: 32000000000, high24hUsd: 64500, low24hUsd: 62800, lastUpdated: '2026-01-01T00:00:00.000Z' },
  { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', priceUsd: 3400, change24hUsd: -45, change24hPercent: -1.3, marketCapUsd: 409000000000, volume24hUsd: 18000000000, high24hUsd: 3460, low24hUsd: 3380, lastUpdated: '2026-01-01T00:00:00.000Z' },
  { id: 'solana', symbol: 'SOL', name: 'Solana', priceUsd: 145, change24hUsd: 6, change24hPercent: 4.3, marketCapUsd: 67000000000, volume24hUsd: 4200000000, high24hUsd: 148, low24hUsd: 139, lastUpdated: '2026-01-01T00:00:00.000Z' },
];

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function sortAssets(items: MarketAsset[], query: MarketQuery): MarketAsset[] {
  const sortBy = query.sortBy ?? 'marketCap';
  const dir = query.sortDirection ?? 'desc';
  const sorted = [...items].sort((a, b) => {
    const va = sortBy === 'price' ? a.priceUsd : sortBy === 'change24h' ? a.change24hPercent : sortBy === 'volume' ? a.volume24hUsd : a.marketCapUsd;
    const vb = sortBy === 'price' ? b.priceUsd : sortBy === 'change24h' ? b.change24hPercent : sortBy === 'volume' ? b.volume24hUsd : b.marketCapUsd;
    return dir === 'asc' ? va - vb : vb - va;
  });
  return sorted;
}

export class MockMarketProvider implements MarketDataProvider {
  async getOverview(): Promise<MarketOverview> {
    await delay(50);
    return {
      totalMarketCapUsd: ASSETS.reduce((s, a) => s + a.marketCapUsd, 0),
      totalVolume24hUsd: ASSETS.reduce((s, a) => s + a.volume24hUsd, 0),
      btcDominancePercent: 52.3,
      ethDominancePercent: 17.1,
      lastUpdated: '2026-01-01T00:00:00.000Z',
    };
  }

  async listAssets(query: MarketQuery = {}): Promise<MarketListResult> {
    await delay(50);
    let items = [...ASSETS];
    if (query.search) {
      const q = query.search.toLowerCase();
      items = items.filter((a) => a.name.toLowerCase().includes(q) || a.symbol.toLowerCase().includes(q));
    }
    items = sortAssets(items, query);
    const offset = query.offset ?? 0;
    const limit = query.limit ?? items.length;
    const page = items.slice(offset, offset + limit);
    return { items: page, total: items.length, query };
  }

  async getAsset(id: string): Promise<MarketAsset | null> {
    await delay(50);
    return ASSETS.find((a) => a.id === id) ?? null;
  }

  async getPriceHistory(id: string, range: PriceHistoryRange): Promise<PriceHistoryResult | null> {
    await delay(50);
    const asset = ASSETS.find((a) => a.id === id);
    if (!asset) return null;
    const counts: Record<PriceHistoryRange, number> = { '1D': 24, '7D': 7, '30D': 30, '90D': 90, '1Y': 12 };
    const n = counts[range];
    const points: PriceHistoryPoint[] = [];
    for (let i = 0; i < n; i++) {
      points.push({ timestamp: `2026-01-01T${String(i).padStart(2, '0')}:00:00.000Z`, priceUsd: asset.priceUsd + (i % 5) * 10 });
    }
    return { assetId: id, range, points, isMock: true };
  }

  async getFreshness(): Promise<MarketFreshness> {
    await delay(10);
    return { source: 'mock', lastUpdated: '2026-01-01T00:00:00.000Z', isStale: false };
  }
}
