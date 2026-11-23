// Guards.jsx: chặn trang theo quyền (giống @member_required / @superuser_required bên Django cũ)
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth';

// chỉ member: chưa đăng nhập thì sang /login, admin thì về trang quản lý
export function RequireMember({ children }) {
  const { user, isAdmin } = useAuth();
  const location = useLocation();
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (isAdmin) return <Navigate to="/admin/users" replace />;
  return children;
}

// chỉ admin: người khác sang /admin/login
export function RequireAdmin({ children }) {
  const { user, isAdmin } = useAuth();
  if (!user || !isAdmin) return <Navigate to="/admin/login" replace />;
  return children;
}
