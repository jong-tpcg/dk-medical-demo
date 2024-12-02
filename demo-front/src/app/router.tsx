import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { NotFoundRoute } from "./routes/NotFound";
import { DashboardLayout } from "./routes/app/DashboardLayout ";
import { Agents } from "@/features/agents/Agents";
import { AgentsChatCommon } from "@/features/agents/AgentsChatCommon";

export const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route path="d-chat" element={<Agents />}>
            <Route path="normal" element={<AgentsChatCommon />} />
            <Route path="insurance" element={<AgentsChatCommon />} />
            <Route path="nursing" element={<AgentsChatCommon />} />
            <Route path="treatment" element={<AgentsChatCommon />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundRoute />} />
      </Routes>
    </Router>
  );
};
