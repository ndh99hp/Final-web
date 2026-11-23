// AdminSidebar.jsx: menu bên trái của các trang quản lý (admin)
import { Link, useLocation } from 'react-router-dom';

export default function AdminSidebar() {
  const { pathname } = useLocation();
  const item = (to, icon, text, active) => (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h4 className="panel-title">
          <Link to={to} style={active ? { color: '#fe980f' } : null}><i className={'fa ' + icon}></i> {text}</Link>
        </h4>
      </div>
    </div>
  );
  return (
    <div className="left-sidebar">
      <h2>Quản lý</h2>
      <div className="panel-group category-products">
        {item('/admin/users', 'fa-users', 'Danh sách user', pathname === '/admin/users' || /^\/admin\/users\/\d+/.test(pathname))}
        {item('/admin/products', 'fa-list', 'Danh sách sản phẩm', pathname.startsWith('/admin/products'))}
        {item('/admin/history', 'fa-shopping-cart', 'Lịch sử mua hàng', pathname === '/admin/history')}
        {item('/admin/users/new', 'fa-plus', 'Tạo superuser', pathname === '/admin/users/new')}
      </div>
    </div>
  );
}
