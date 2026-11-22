import type {Metadata} from 'next';
import {notFound} from 'next/navigation';
import {NextIntlClientProvider} from 'next-intl';
import {locales} from '@/i18n';
import '../globals.css';

export const metadata: Metadata = {
  title: 'Crypto Intelligence Platform',
  description: 'Smart Money & Trader Intelligence System'
};

type LocaleLayoutProps = {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
};

export default async function LocaleLayout({
  children,
  params
}: LocaleLayoutProps) {
  const {locale} = await params;
  if (!locales.includes(locale as (typeof locales)[number])) {
    notFound();
  }
  const dir = locale === 'fa' ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir}>
      <body>
        <NextIntlClientProvider locale={locale}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
