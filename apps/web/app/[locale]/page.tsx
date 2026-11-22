import {useTranslations} from 'next-intl';

export default function Home() {
  const t = useTranslations('Home');
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <p className="text-[#929BAA] mt-2">{t('subtitle')}</p>
    </main>
  );
}
