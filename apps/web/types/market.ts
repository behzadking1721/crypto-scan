export type MarketAsset = {
  id: string;
  symbol: string;
  name: string;
  priceUsd: number;
  change24hUsd: number;
  change24hPercent: number;
  marketCapUsd: number;
  volume24hUsd: number;
  high24hUsd: number;
  low24hUsd: number;
  lastUpdated: string;
};

export type MarketOverview = {
  totalMarketCapUsd: number;
  totalVolume24hUsd: number;
  btcDominancePercent: number;
  ethDominancePercent: number;
  lastUpdated: string;
};

export type MarketQuery = {
  search?: string;
  sortBy?: 'marketCap' | 'price' | 'change24h' | 'volume';
  sortDirection?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
};

export type MarketListResult = {
  items: MarketAsset[];
  total: number;
  query: MarketQuery;
};

export type MarketFreshness = {
  source: string;
  lastUpdated: string;
  isStale: boolean;
};

export type PriceHistoryRange = '1D' | '7D' | '30D' | '90D' | '1Y';

export type PriceHistoryPoint = {
  timestamp: string;
  priceUsd: number;
};

export type PriceHistoryResult = {
  assetId: string;
  range: PriceHistoryRange;
  points: PriceHistoryPoint[];
  isMock: true;
};

export type MarketDataProvider = {
  getOverview(): Promise<MarketOverview>;
  listAssets(query?: MarketQuery): Promise<MarketListResult>;
  getAsset(id: string): Promise<MarketAsset | null>;
  getFreshness(): Promise<MarketFreshness>;
  getPriceHistory(id: string, range: PriceHistoryRange): Promise<PriceHistoryResult | null>;
};
