import React, { useState, createContext, useContext } from 'react';

interface Tab {
  id: string;
  label: string;
  disabled?: boolean;
}

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
  children: React.ReactNode;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, defaultTab, onChange, children }) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || '');

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab: handleTabChange }}>
      <div>
        <div className="tabs" role="tablist">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`tabpanel-${tab.id}`}
              disabled={tab.disabled}
              onClick={() => !tab.disabled && handleTabChange(tab.id)}
              className={`tab ${activeTab === tab.id ? 'tab-active' : ''} ${tab.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </TabsContext.Provider>
  );
};

interface TabPanelProps {
  tabId: string;
  children: React.ReactNode;
}

export const TabPanel: React.FC<TabPanelProps> = ({ tabId, children }) => {
  const context = useContext(TabsContext);

  if (!context) {
    throw new Error('TabPanel must be used within Tabs');
  }

  if (context.activeTab !== tabId) {
    return null;
  }

  return (
    <div
      role="tabpanel"
      id={`tabpanel-${tabId}`}
      aria-labelledby={tabId}
      className="animate-fade-in"
    >
      {children}
    </div>
  );
};

export default Tabs;
