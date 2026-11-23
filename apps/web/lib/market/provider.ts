import type {
  MarketAsset,
  MarketFreshness,
  MarketListResult,
  MarketOverview,
  MarketQuery,
  PriceHistoryRange,
  PriceHistoryResult,
} from '../../types/market';

export type MarketDataProvider = {
  getOverview(): Promise<MarketOverview>;
  listAssets(query?: MarketQuery): Promise<MarketListResult>;
  getAsset(id: string): Promise<MarketAsset | null>;
  getFreshness(): Promise<MarketFreshness>;
  getPriceHistory(id: string, range: PriceHistoryRange): Promise<PriceHistoryResult | null>;
};
