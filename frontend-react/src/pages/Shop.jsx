// Shop.jsx: trang cửa hàng - lọc theo danh mục, thương hiệu, khoảng giá, sắp xếp, phân trang
// Điều kiện lọc lưu trên URL (?q=&category=&brand=&price=&sort=&page=) nên bấm Back vẫn đúng
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api';
import ProductCard from '../components/ProductCard';
import Sidebar from '../components/Sidebar';
import PriceSlider from '../components/PriceSlider';
import Pagination from '../components/Pagination';

export default function Shop() {
  const [params, setParams] = useSearchParams();
  const [filters, setFilters] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const q = params.get('q') || '';
  const category = params.get('category') || '';
  const brand = params.get('brand') || '';
  const price = params.get('price') || '';
  const sort = params.get('sort') || '';
  const page = params.get('page') || '1';

  useEffect(() => {
    api('/filters/').then(setFilters).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    api('/products/', { params: { q, category, brand, price, sort, page } })
      .then((d) => { setData(d); setError(''); })
      .catch((e) => setError(e.message));
  }, [q, category, brand, price, sort, page]);

  // đổi 1 điều kiện lọc: các điều kiện khác giữ nguyên, về trang 1
  function change(name, value) {
    const next = new URLSearchParams(params);
    if (value === '' || value === null) next.delete(name);
    else next.set(name, value);
    if (name !== 'page') next.delete('page');
    setParams(next);
  }

  const max = filters ? filters.slider_max : 100;
  const [low, high] = price ? price.split(',').map(Number) : [0, max];

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3">
            <Sidebar filters={filters} categoryId={category} brandId={brand}
              onCategory={(v) => change('category', v)} onBrand={(v) => change('brand', v)}>
              <PriceSlider max={max} low={low} high={high}
                onCommit={(r) => change('price', r[0] === 0 && r[1] === max ? '' : r[0] + ',' + r[1])} />
            </Sidebar>
          </div>

          <div className="col-sm-9 padding-right">
            <div className="features_items">
              <h2 className="title text-center">Tất cả sản phẩm</h2>

              <div className="col-sm-12" style={{ marginBottom: 20 }}>
                <div className="row">
                  <div className="col-sm-6">
                    {q && <span>Kết quả cho: <b>"{q}"</b> <a className="cursor" onClick={() => change('q', '')}>[xóa]</a></span>}
                    {data && <span className="text-muted"> ({data.count} sản phẩm)</span>}
                  </div>
                  <div className="col-sm-6">
                    <select className="form-control" value={sort} onChange={(e) => change('sort', e.target.value)}>
                      <option value="">Sắp xếp mặc định</option>
                      {(filters ? filters.sort_options : []).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </div>
                </div>
              </div>

              {error && <div className="col-sm-12"><div className="alert alert-danger">{error}</div></div>}
              {data && data.results.length === 0 && <p className="text-center">Không tìm thấy sản phẩm phù hợp.</p>}
              {data && data.results.map((p) => <ProductCard key={p.id} p={p} />)}
              <Pagination data={data} onChange={(p) => change('page', p)} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
