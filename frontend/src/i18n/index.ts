import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enUS from './locales/en-US.json';
import esES from './locales/es-ES.json';
import frFR from './locales/fr-FR.json';
import deDE from './locales/de-DE.json';
import jaJP from './locales/ja-JP.json';

const resources = {
  'en-US': { translation: enUS },
  'es-ES': { translation: esES },
  'fr-FR': { translation: frFR },
  'de-DE': { translation: deDE },
  'ja-JP': { translation: jaJP },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en-US',
    supportedLngs: ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'ja-JP'],
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

export const languages = [
  { code: 'en-US', name: 'English', nativeName: 'English', direction: 'ltr' as const },
  { code: 'es-ES', name: 'Spanish', nativeName: 'Español', direction: 'ltr' as const },
  { code: 'fr-FR', name: 'French', nativeName: 'Français', direction: 'ltr' as const },
  { code: 'de-DE', name: 'German', nativeName: 'Deutsch', direction: 'ltr' as const },
  { code: 'ja-JP', name: 'Japanese', nativeName: '日本語', direction: 'ltr' as const },
];

export default i18n;
