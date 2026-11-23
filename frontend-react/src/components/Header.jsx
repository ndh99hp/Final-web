// Header.jsx: đầu trang (logo + menu tài khoản / giỏ hàng + menu chính + ô tìm kiếm)
import { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth';
import { useCart } from '../cart';

export default function Header() {
  const { user, isAdmin, isMember, logout } = useAuth();
  const { count } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [keyword, setKeyword] = useState('');

  async function handleLogout() {
    const wasAdmin = isAdmin;
    await logout();
    navigate(wasAdmin ? '/admin/login' : '/login');
  }

  // gõ từ khóa rồi Enter: sang trang shop và lọc theo tên
  function handleSearch(e) {
    e.preventDefault();
    navigate('/shop?q=' + encodeURIComponent(keyword.trim()));
  }

  // NavLink tự thêm class "active" khi đang ở đúng trang
  const act = ({ isActive }) => (isActive ? 'active' : '');

  return (
    <header id="header">
      {/* ===== 1. Phần giữa: logo + menu tài khoản ===== */}
      <div className="header-middle">
        <div className="container">
          <div className="row">
            <div className="col-md-4 clearfix">
              <div className="logo pull-left">
                <Link to="/"><img src="/images/home/logo.png" alt="E-Shopper" /></Link>
              </div>
            </div>
            <div className="col-md-8 clearfix">
              <div className="shop-menu clearfix pull-right">
                <ul className="nav navbar-nav">
                  {/* phân quyền: admin thấy menu quản trị, member thấy menu tài khoản */}
                  {isAdmin && (
                    <>
                      <li><Link to="/admin/users"><i className="fa fa-user"></i> Xin chào, {user.username} (Admin)</Link></li>
                      <li><NavLink to="/admin/users" className={act}><i className="fa fa-users"></i> Quản lý</NavLink></li>
                    </>
                  )}
                  {isMember && (
                    <>
                      <li><NavLink to="/account" end className={act}><i className="fa fa-user"></i> Xin chào, {user.username}</NavLink></li>
                      <li><NavLink to="/account/my-product" className={act}><i className="fa fa-list"></i> Sản phẩm của tôi</NavLink></li>
                    </>
                  )}
                  {!isAdmin && (
                    <>
                      <li><NavLink to="/checkout" className={act}><i className="fa fa-crosshairs"></i> Thanh toán</NavLink></li>
                      <li><NavLink to="/cart" className={act}><i className="fa fa-shopping-cart"></i> Giỏ hàng (<span id="cart-counter">{count}</span>)</NavLink></li>
                    </>
                  )}
                  {user ? (
                    <li><a className="cursor" onClick={handleLogout}><i className="fa fa-sign-out"></i> Đăng xuất</a></li>
                  ) : (
                    <>
                      <li><NavLink to="/login" className={act}><i className="fa fa-lock"></i> Đăng nhập</NavLink></li>
                      <li><NavLink to="/register" className={act}><i className="fa fa-plus"></i> Đăng ký</NavLink></li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ===== 2. Menu chính + ô tìm kiếm ===== */}
      <div className="header-bottom">
        <div className="container">
          <div className="row">
            <div className="col-sm-9">
              <div className="navbar-header">
                <button type="button" className="navbar-toggle" onClick={() => setMenuOpen(!menuOpen)}>
                  <span className="sr-only">Toggle navigation</span>
                  <span className="icon-bar"></span>
                  <span className="icon-bar"></span>
                  <span className="icon-bar"></span>
                </button>
              </div>
              <div className="mainmenu pull-left">
                <ul className={'nav navbar-nav collapse navbar-collapse' + (menuOpen ? ' in' : '')}>
                  <li><NavLink to="/" end className={act}>Trang chủ</NavLink></li>
                  <li className="dropdown">
                    <NavLink to="/shop" className={act}>Cửa hàng <i className="fa fa-angle-down"></i></NavLink>
                    <ul role="menu" className="sub-menu">
                      <li><Link to="/shop">Tất cả sản phẩm</Link></li>
                      {!user && <li><Link to="/login">Đăng nhập</Link></li>}
                      {isMember && <li><Link to="/account/my-product">Sản phẩm của tôi</Link></li>}
                      {isMember && <li><Link to="/account/add-product">Thêm sản phẩm</Link></li>}
                      {!isAdmin && <li><Link to="/cart">Giỏ hàng</Link></li>}
                      {!isAdmin && <li><Link to="/checkout">Thanh toán</Link></li>}
                    </ul>
                  </li>
                  <li className="dropdown">
                    <NavLink to="/blog" className={act}>Blog <i className="fa fa-angle-down"></i></NavLink>
                    <ul role="menu" className="sub-menu">
                      <li><Link to="/blog">Danh sách Blog</Link></li>
                    </ul>
                  </li>
                  <li><NavLink to="/contact" className={act}>Liên hệ</NavLink></li>
                  <li><NavLink to="/search-advanced" className={act}>Tìm kiếm nâng cao</NavLink></li>
                </ul>
              </div>
            </div>
            <div className="col-sm-3">
              <form onSubmit={handleSearch} className="search_box pull-right">
                <input type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Tìm kiếm sản phẩm" />
              </form>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
