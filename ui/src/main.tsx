import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GrowthBook, GrowthBookProvider } from "@growthbook/growthbook-react";

// Create a GrowthBook instance
const gb = new GrowthBook({
  apiHost: "https://cdn.growthbook.io",
  clientKey: import.meta.env.VITE_GROWTHBOOK_CLIENT_KEY,
  enableDevMode: import.meta.env.DEV,
  attributes: {
    id: "anonymous",
    loggedIn: false,
    employee: false,
    country: "unknown",
  },
  trackingCallback: (experiment, result) => {
    // TODO: Log experiment data to analytics
    console.log("Experiment Viewed", {
      experimentId: experiment.key,
      variationId: result.variationId,
    });
  },
});


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GrowthBookProvider growthbook={gb}>
      <App />
    </GrowthBookProvider>
  </StrictMode>,
)

// Load features asynchronously
gb.loadFeatures();
