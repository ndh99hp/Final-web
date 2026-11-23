// ProductDetail.jsx: chi tiết 1 sản phẩm (hình nhỏ, phóng to, số lượng, sản phẩm liên quan)
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { useCart } from '../cart';
import { DEFAULT_IMAGE, money } from '../format';
import ProductCard from '../components/ProductCard';

export default function ProductDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [current, setCurrent] = useState(0); // hình đang xem
  const [qty, setQty] = useState(1);
  const [zoom, setZoom] = useState(false);

  useEffect(() => {
    setData(null);
    setCurrent(0);
    setQty(1);
    api('/products/' + id + '/').then(setData).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <section><div className="container"><div className="alert alert-danger">{error}</div><Link to="/shop">Về cửa hàng</Link></div></section>;
  if (!data) return <section><div className="container"><p>Đang tải...</p></div></section>;

  const p = data.product;
  const images = p.images.length ? p.images : [DEFAULT_IMAGE];
  const isOwner = user && p.author === user.id;

  async function handleDelete() {
    if (!window.confirm('Xóa sản phẩm "' + p.title + '"?')) return;
    try {
      await api('/my-products/delete/' + p.id + '/', { method: 'DELETE' });
      navigate('/account/my-product');
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-12">
            <div className="product-details">
              <div className="col-sm-5">
                <div className="view-product">
                  <img src={images[current]} alt={p.title} style={{ width: '100%', cursor: 'zoom-in' }} onClick={() => setZoom(true)} />
                  <h3>Bấm vào hình để phóng to</h3>
                </div>
                <div style={{ marginTop: 10 }}>
                  {images.map((url, i) => (
                    <img key={url} src={url} alt="" onClick={() => setCurrent(i)}
                      style={{ width: 80, height: 80, objectFit: 'cover', marginRight: 8, cursor: 'pointer', border: i === current ? '2px solid #fe980f' : '2px solid #f0f0e9' }} />
                  ))}
                </div>
              </div>

              <div className="col-sm-7">
                <div className="product-information">
                  <img src={p.status === 1 ? '/images/home/sale.png' : '/images/home/new.png'} className="newarrival" alt="" />
                  <h2>{p.title}</h2>
                  <p>Mã sản phẩm: {p.id}</p>
                  <span>
                    {p.status === 1 ? (
                      <span>${money(p.sale)} <del style={{ fontSize: 18, color: '#999' }}>${money(p.price)}</del></span>
                    ) : (
                      <span>${money(p.price)}</span>
                    )}
                    <label>Số lượng:</label>
                    <input type="number" min="1" max="99" value={qty} onChange={(e) => setQty(Math.max(1, Math.min(99, Number(e.target.value) || 1)))} />
                    <button type="button" className="btn btn-fefault cart" onClick={() => addToCart(p.id, qty)}>
                      <i className="fa fa-shopping-cart"></i> Thêm vào giỏ
                    </button>
                  </span>
                  <p><b>Trạng thái:</b> {p.status === 1 ? 'Đang giảm giá' : 'Hàng mới'}</p>
                  <p><b>Danh mục:</b> {p.category_name || 'Chưa có'}</p>
                  <p><b>Thương hiệu:</b> {p.brand_name || 'Chưa có'}</p>
                  <p><b>Công ty:</b> {p.company || 'Chưa có'}</p>
                  <p><b>Người đăng:</b> {p.author_name}</p>
                  {isOwner && (
                    <p>
                      <Link to={'/account/edit-product/' + p.id} className="btn btn-default">Sửa</Link>{' '}
                      <button className="btn btn-danger" onClick={handleDelete}>Xóa</button>
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="category-tab shop-details-tab">
              <div className="col-sm-12">
                <ul className="nav nav-tabs"><li className="active"><a>Mô tả chi tiết</a></li></ul>
              </div>
              <div className="tab-content">
                <div className="tab-pane fade active in" style={{ padding: 20, whiteSpace: 'pre-line' }}>
                  {p.detail || 'Sản phẩm chưa có mô tả.'}
                </div>
              </div>
            </div>

            {data.related.length > 0 && (
              <div className="recommended_items">
                <h2 className="title text-center">Sản phẩm liên quan</h2>
                <div className="row">
                  {data.related.map((r) => <ProductCard key={r.id} p={r} />)}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {zoom && (
        <div onClick={() => setZoom(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.8)', zIndex: 9998, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'zoom-out' }}>
          <img src={images[current]} alt="" style={{ maxWidth: '90%', maxHeight: '90%' }} />
        </div>
      )}
    </section>
  );
}
