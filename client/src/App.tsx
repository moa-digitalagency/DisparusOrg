import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/lib/theme";
import { OfflineIndicator } from "@/components/OfflineIndicator";
import NotFound from "@/pages/not-found";
import Landing from "@/pages/Landing";
import Search from "@/pages/Search";
import ReportForm from "@/pages/ReportForm";
import DisparuDetail from "@/pages/DisparuDetail";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <Route path="/recherche" component={Search} />
      <Route path="/signaler" component={ReportForm} />
      <Route path="/disparu/:id" component={DisparuDetail} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="disparus-theme">
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <OfflineIndicator />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
