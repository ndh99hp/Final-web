// Footer.jsx: chân trang
import { Link } from 'react-router-dom';
import { useAuth } from '../auth';

export default function Footer() {
  const { user, isAdmin, isMember } = useAuth();
  return (
    <footer id="footer">
      <div className="footer-widget">
        <div className="container">
          <div className="row">
            <div className="col-sm-4">
              <div className="companyinfo">
                <h2><span>e</span>-shopper</h2>
                <p>Đồ án Web Bao Vic - Trang thương mại điện tử mua bán sản phẩm.</p>
              </div>
            </div>
            <div className="col-sm-2 col-sm-offset-2">
              <div className="single-widget">
                <h2>Mua sắm</h2>
                <ul className="nav nav-pills nav-stacked">
                  <li><Link to="/">Trang chủ</Link></li>
                  <li><Link to="/shop">Tất cả sản phẩm</Link></li>
                  {!isAdmin && <li><Link to="/cart">Giỏ hàng</Link></li>}
                  <li><Link to="/blog">Blog</Link></li>
                </ul>
              </div>
            </div>
            <div className="col-sm-2">
              <div className="single-widget">
                <h2>Tài khoản</h2>
                <ul className="nav nav-pills nav-stacked">
                  {isAdmin && <li><Link to="/admin/users">Trang quản lý</Link></li>}
                  {isMember && <li><Link to="/account">Cập nhật thông tin</Link></li>}
                  {isMember && <li><Link to="/account/my-product">Sản phẩm của tôi</Link></li>}
                  {isMember && <li><Link to="/account/add-product">Thêm sản phẩm</Link></li>}
                  {!user && <li><Link to="/login">Đăng nhập</Link></li>}
                  {!user && <li><Link to="/register">Đăng ký</Link></li>}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <div className="container">
          <div className="row">
            <p className="pull-left">Copyright &copy; 2026 Đồ Án Web Bao Vic. All rights reserved.</p>
            <p className="pull-right">Giao diện: <span><a target="_blank" rel="noreferrer" href="http://www.themeum.com">E-Shopper - Themeum</a></span></p>
          </div>
        </div>
      </div>
    </footer>
  );
}
