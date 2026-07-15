import { Navigate, Route, Routes } from "react-router-dom";
import { RequireAuth } from "./auth/RequireAuth";
import { RequireAdmin } from "./auth/RequireAdmin";
import { AppLayout } from "./layout/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { PlansListPage } from "./pages/PlansListPage";
import { UploadPlanPage } from "./pages/UploadPlanPage";
import { PlanDetailPage } from "./pages/PlanDetailPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { RegisterPage } from "./pages/RegisterPage";
function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage/>}/>
            <Route path="/register" element={<RegisterPage/>}/>
            <Route element={<RequireAuth/>}>
                <Route element={<AppLayout/>}>
                    <Route path="/" element={<Navigate to="/plans" replace/>}/>
                    <Route path="/plans" element={<PlansListPage/>}/>
                    <Route path="/plans/new" element={<UploadPlanPage/>}/>
                    <Route path="/plans/:planId" element={<PlanDetailPage/>}/>
                    <Route element={<RequireAdmin/>}>
                        <Route path="/admin/users" element={<AdminUsersPage/>}/>
                    </Route>
                    <Route path="/logout" element={<Navigate to="/login" replace/>}/>
                </Route>
            </Route>
            <Route path="*" element={<Navigate to="/plans" replace/>}/>
        </Routes>
    );
}
export default App;