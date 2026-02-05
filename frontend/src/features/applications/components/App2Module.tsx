import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ModuleLayout } from '@/components/modules';
import { SummaryPage } from './SummaryPage';
import { InsightsPage } from './InsightsPage';
import { DataPage } from './DataPage';
import { ActionsPage } from './ActionsPage';
import { SettingsPage } from './SettingsPage';

export const App2Module: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Routes>
      <Route element={<ModuleLayout basePath="/app2" title={t('nav.app2')} />}>
        <Route index element={<SummaryPage appName="Application 2" />} />
        <Route path="insights" element={<InsightsPage appName="Application 2" />} />
        <Route path="data" element={<DataPage appName="Application 2" />} />
        <Route path="actions" element={<ActionsPage appName="Application 2" />} />
        <Route path="settings" element={<SettingsPage appName="Application 2" />} />
      </Route>
    </Routes>
  );
};

export default App2Module;
