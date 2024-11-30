import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { NotFoundRoute } from "./routes/NotFound";
import { DashboardLayout } from "./routes/app/DashboardLayout ";
import { Agents } from "@/features/agents/Agents";

export const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route path="d-chat" element={<Agents />} />
        </Route>
        <Route path="*" element={<NotFoundRoute />} />
      </Routes>
    </Router>
  );
};
