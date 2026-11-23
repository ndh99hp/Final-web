// Home.jsx: trang chủ - 6 sản phẩm mới nhất
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import ProductCard from '../components/ProductCard';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api('/home/').then((d) => setProducts(d.results)).catch(() => {}).finally(() => setLoading(false));
    api('/filters/').then(setFilters).catch(() => {});
  }, []);

  return (
    <>
      <section id="slider">
        <div className="container">
          <div className="row">
            <div className="col-sm-12">
              <div className="slider-box" style={{ background: '#f0f0e9', padding: '60px 40px', marginBottom: 30 }}>
                <h1><span>E</span>-SHOPPER</h1>
                <h2>Mua sắm trực tuyến</h2>
                <p>Hàng ngàn sản phẩm do các thành viên đăng bán, giá tốt mỗi ngày.</p>
                <Link to="/shop" className="btn btn-default get">Xem cửa hàng</Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="container">
          <div className="row">
            <div className="col-sm-3">
              <div className="left-sidebar">
                <h2>Danh mục</h2>
                <div className="panel-group category-products">
                  {(filters ? filters.categories : []).map((c) => (
                    <div className="panel panel-default" key={c.id}>
                      <div className="panel-heading">
                        <h4 className="panel-title"><Link to={'/shop?category=' + c.id}><span className="badge pull-right">{c.total}</span>{c.name}</Link></h4>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="brands_products">
                  <h2>Thương hiệu</h2>
                  <div className="brands-name">
                    <ul className="nav nav-pills nav-stacked">
                      {(filters ? filters.brands : []).map((b) => (
                        <li key={b.id}><Link to={'/shop?brand=' + b.id}><span className="pull-right">({b.total})</span>{b.name}</Link></li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-sm-9 padding-right">
              <div className="features_items">
                <h2 className="title text-center">Sản phẩm mới nhất</h2>
                {loading && <p className="text-center">Đang tải...</p>}
                {!loading && products.length === 0 && <p className="text-center">Chưa có sản phẩm nào.</p>}
                {products.map((p) => <ProductCard key={p.id} p={p} />)}
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
