import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ModuleLayout } from '@/components/modules';
import { SummaryPage } from './SummaryPage';
import { InsightsPage } from './InsightsPage';
import { DataPage } from './DataPage';
import { ActionsPage } from './ActionsPage';
import { SettingsPage } from './SettingsPage';

export const App3Module: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Routes>
      <Route element={<ModuleLayout basePath="/app3" title={t('nav.app3')} />}>
        <Route index element={<SummaryPage appName="Application 3" />} />
        <Route path="insights" element={<InsightsPage appName="Application 3" />} />
        <Route path="data" element={<DataPage appName="Application 3" />} />
        <Route path="actions" element={<ActionsPage appName="Application 3" />} />
        <Route path="settings" element={<SettingsPage appName="Application 3" />} />
      </Route>
    </Routes>
  );
};

export default App3Module;
