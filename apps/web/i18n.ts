import {getRequestConfig} from 'next-intl/server';
import {notFound} from 'next/navigation';

export const locales = ['en', 'fa'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

type HomeMessages = {
  Home: {
    title: string;
    subtitle: string;
  };
};

const messages: Record<Locale, HomeMessages> = {
  en: (await import('./messages/en.json')).default,
  fa: (await import('./messages/fa.json')).default
};

export default getRequestConfig(async ({locale}: {locale: string}) => {
  if (!locales.includes(locale as Locale)) {
    notFound();
  }
  return {
    messages: messages[locale as Locale]
  };
});
