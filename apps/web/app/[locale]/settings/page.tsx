import {getTranslations} from 'next-intl/server';
import {locales} from '@/i18n';

export default async function SettingsPage({params}: {params: Promise<{locale: string}>}) {
  const {locale} = await params;
  const t = await getTranslations('Settings');
  return (
    <main className="min-h-screen p-6 space-y-4">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <div className="rounded border p-4">
        <div className="font-medium">{t('language')}</div>
        <div className="mt-2 flex gap-2">
          {locales.map((l) => (
            <a key={l} href={`/${l}/settings`} className={`px-3 py-1 border rounded ${l === locale ? 'bg-blue-600 text-white' : ''}`}>{l}</a>
          ))}
        </div>
      </div>
      <div className="rounded border p-4">
        <div className="font-medium">{t('dataSource')}</div>
        <div className="text-sm text-gray-500">{t('mockSource')}</div>
      </div>
    </main>
  );
}
