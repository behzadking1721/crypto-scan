'use client';

import { useEffect, useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { ApiError, fetchHealth, fetchReady, mapDependencyStatus, mapOverallStatus, HealthResponse, HealthStatus } from '@/lib/api';
import { StatusCard } from '@/components/health/StatusCard';

export default function HealthPage() {
  const t = useTranslations('Health');

  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [backendStatus, setBackendStatus] = useState<HealthStatus>('checking');
  const [isReady, setIsReady] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [lastAttempt, setLastAttempt] = useState<Date | null>(null);

  const checkHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    setLastAttempt(new Date());

    try {
      const [health] = await Promise.all([fetchHealth(), fetchReady()]);
      setHealthData(health);
      setBackendStatus('healthy');
      setIsReady(true);
      setLastCheck(new Date());
    } catch (err) {
      setHealthData(null);
      setIsReady(null);

      if (err instanceof ApiError) {
        if (err.code === 'network_error') {
          setBackendStatus('unknown');
          setError(t('unableToConnect'));
        } else if (err.code === 'timeout') {
          setBackendStatus('unknown');
          setError(t('requestTimeout'));
        } else {
          setBackendStatus('unknown');
          setError(err.message);
        }
      } else {
        setBackendStatus('unknown');
        setError(t('unableToConnect'));
      }
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  const overallStatus = mapOverallStatus(healthData?.status);
  const postgresStatus = mapDependencyStatus(healthData?.dependencies.postgresql.status);
  const redisStatus = mapDependencyStatus(healthData?.dependencies.redis.status);
  const postgresError = healthData?.dependencies.postgresql.error;
  const redisError = healthData?.dependencies.redis.error;

  const readinessStatus: HealthStatus = isReady === true ? 'healthy' : isReady === false ? 'unhealthy' : 'unknown';

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-2xl font-bold text-[var(--text)]">{t('title')}</h1>
          <p className="text-[var(--text-secondary)] mt-1">{t('subtitle')}</p>
        </header>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-[var(--text)] mb-4">{t('overview')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatusCard labelKey="overallStatus" status={overallStatus} />
            <StatusCard labelKey="backendConnectivity" status={backendStatus} />
            <StatusCard labelKey="readinessStatus" status={readinessStatus} />
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-lg font-semibold text-[var(--text)] mb-4">{t('dependencies')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatusCard labelKey="backendApi" status={backendStatus} />
            <StatusCard labelKey="postgresql" status={postgresStatus} error={postgresError} />
            <StatusCard labelKey="redis" status={redisStatus} error={redisError} />
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-[var(--text)] mb-4">{t('monitoringControls')}</h2>
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
            <button
              onClick={checkHealth}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-[var(--secondary)] border border-[var(--secondary)] rounded text-[var(--text)] hover:bg-[var(--text-secondary)] disabled:opacity-50 transition-colors text-sm font-medium"
            >
              {loading ? t('checkingData') : t('refresh')}
            </button>
            <div className="text-sm text-[var(--text-secondary)] space-y-1">
              <div>{t('lastCheck')}: {lastCheck ? lastCheck.toLocaleTimeString() : t('notAvailable')}</div>
              <div>{t('lastAttempt')}: {lastAttempt ? lastAttempt.toLocaleTimeString() : t('notAvailable')}</div>
            </div>
          </div>
          {error && (
            <div className="mt-4 p-4 bg-[var(--negative)]/10 border border-[var(--negative)]/30 rounded text-[var(--negative)] text-sm">
              {error}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
