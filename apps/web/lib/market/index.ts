import type { MarketDataProvider } from './provider';
import { MockMarketProvider } from './mock-provider';

export function getMarketDataProvider(): MarketDataProvider {
  return new MockMarketProvider();
}
