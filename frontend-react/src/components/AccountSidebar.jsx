// AccountSidebar.jsx: menu bên trái của các trang Account (member)
import { Link, useLocation } from 'react-router-dom';

export default function AccountSidebar() {
  const { pathname } = useLocation();
  const item = (to, text, active) => (
    <div className="panel panel-default">
      <div className="panel-heading">
        <h4 className="panel-title"><Link to={to} style={active ? { color: '#fe980f' } : null}>{text}</Link></h4>
      </div>
    </div>
  );
  return (
    <div className="left-sidebar">
      <h2>Tài khoản</h2>
      <div className="panel-group category-products">
        {item('/account', 'Cập nhật thông tin', pathname === '/account')}
        {item('/orders', 'Lịch sử mua hàng', pathname === '/orders')}
      </div>
      <h2>Sản phẩm</h2>
      <div className="panel-group category-products">
        {item('/account/my-product', 'Sản phẩm của tôi', pathname === '/account/my-product' || pathname.startsWith('/account/edit-product'))}
        {item('/account/add-product', 'Thêm sản phẩm', pathname === '/account/add-product')}
      </div>
    </div>
  );
}
