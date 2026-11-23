// ProductCard.jsx: thẻ 1 sản phẩm (dùng ở trang chủ, shop, tìm kiếm, sản phẩm liên quan)
import { Link } from 'react-router-dom';
import { useCart } from '../cart';
import { DEFAULT_IMAGE, money } from '../format';

export default function ProductCard({ p }) {
  const { addToCart } = useCart();
  const image = p.image || DEFAULT_IMAGE;
  const onSale = p.status === 1;

  function handleAdd(e) {
    e.preventDefault();
    addToCart(p.id, 1);
  }

  return (
    <div className="col-sm-4">
      <div className="product-image-wrapper">
        <div className="single-products">
          <div className="productinfo text-center">
            <Link to={'/shop/' + p.id}>
              <img src={image} alt={p.title} style={{ width: '100%', height: 250, objectFit: 'cover' }} />
            </Link>
            {onSale ? (
              <h2>${money(p.sale)} <del style={{ fontSize: 16, color: '#999' }}>${money(p.price)}</del></h2>
            ) : (
              <h2>${money(p.price)}</h2>
            )}
            <p><Link to={'/shop/' + p.id} style={{ color: 'inherit' }}>{p.title}</Link></p>
            <a href="#" className="btn btn-default" onClick={handleAdd}><i className="fa fa-shopping-cart"></i> Thêm vào giỏ</a>
          </div>
          {/* lớp phủ hiện ra khi rê chuột vào sản phẩm */}
          <div className="product-overlay">
            <div className="overlay-content">
              <h2>${money(p.final_price)}</h2>
              <p>{p.title}</p>
              <a href="#" className="btn btn-default add-to-cart" onClick={handleAdd}><i className="fa fa-shopping-cart"></i> Thêm vào giỏ</a>
              <Link to={'/shop/' + p.id} className="btn btn-default add-to-cart"><i className="fa fa-eye"></i> Xem chi tiết</Link>
            </div>
          </div>
          <img src={onSale ? '/images/home/sale.png' : '/images/home/new.png'} className="new" alt={onSale ? 'Sale' : 'New'} />
        </div>
        <div className="choose">
          <ul className="nav nav-pills nav-justified">
            <li><Link to={p.category ? '/shop?category=' + p.category : '#'}><i className="fa fa-tag"></i> {p.category_name || 'Chưa có danh mục'}</Link></li>
            <li><Link to={p.brand ? '/shop?brand=' + p.brand : '#'}><i className="fa fa-star"></i> {p.brand_name || 'Chưa có hãng'}</Link></li>
          </ul>
        </div>
      </div>
    </div>
  );
}
