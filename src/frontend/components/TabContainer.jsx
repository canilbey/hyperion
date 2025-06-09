import React from "react";

const TabContainer = ({ tabs, selectedTab, setSelectedTab, children }) => (
  <div className="flex flex-col w-full h-full">
    <div className="flex border-b bg-white">
      {tabs.map((tab) => (
        <button
          key={tab}
          className={`px-6 py-3 text-sm font-medium transition border-b-2 -mb-px ${selectedTab === tab ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-blue-500'}`}
          onClick={() => setSelectedTab(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
    <div className="flex-1 overflow-auto bg-gray-50 p-6">{children}</div>
  </div>
);

export default TabContainer; 