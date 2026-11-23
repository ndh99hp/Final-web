// SearchAdvanced.jsx: tìm kiếm nâng cao (tên + khoảng giá + danh mục + hãng + trạng thái)
import { useEffect, useState } from 'react';
import { api } from '../api';
import ProductCard from '../components/ProductCard';
import Pagination from '../components/Pagination';

const EMPTY = { name: '', price: '', category: '', brand: '', status: '' };

export default function SearchAdvanced() {
  const [filters, setFilters] = useState(null);
  const [form, setForm] = useState(EMPTY);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/filters/').then(setFilters).catch(() => {});
  }, []);

  async function search(page = 1, values = form) {
    try {
      setData(await api('/products/search/', { params: { ...values, page } }));
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    search(1);
  }

  function handleReset() {
    setForm(EMPTY);
    setData(null);
  }

  const gap = { marginBottom: 12 };
  return (
    <section>
      <div className="container">
        <h2 className="title text-center">Tìm kiếm nâng cao</h2>
        <form onSubmit={handleSubmit} className="box">
          <div className="row">
            <div className="col-sm-4">
              <input type="text" name="name" className="form-control" placeholder="Tên sản phẩm" value={form.name} onChange={setField} style={gap} />
            </div>
            <div className="col-sm-4">
              <select name="price" className="form-control" value={form.price} onChange={setField} style={gap}>
                <option value="">Tất cả mức giá</option>
                {(filters ? filters.price_ranges : []).map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
            <div className="col-sm-4">
              <select name="status" className="form-control" value={form.status} onChange={setField} style={gap}>
                <option value="">Tất cả trạng thái</option>
                <option value="0">New</option>
                <option value="1">Sale</option>
              </select>
            </div>
            <div className="col-sm-4">
              <select name="category" className="form-control" value={form.category} onChange={setField} style={gap}>
                <option value="">Tất cả danh mục</option>
                {(filters ? filters.categories : []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="col-sm-4">
              <select name="brand" className="form-control" value={form.brand} onChange={setField} style={gap}>
                <option value="">Tất cả thương hiệu</option>
                {(filters ? filters.brands : []).map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div className="col-sm-4">
              <button type="submit" className="btn btn-primary">Tìm kiếm</button>{' '}
              <button type="button" className="btn btn-default" onClick={handleReset}>Xóa</button>
            </div>
          </div>
        </form>

        {error && <div className="alert alert-danger">{error}</div>}
        {data && (
          <div className="features_items">
            <p className="text-muted">Tìm thấy {data.count} sản phẩm</p>
            {data.results.length === 0 && <p className="text-center">Không có sản phẩm phù hợp.</p>}
            {data.results.map((p) => <ProductCard key={p.id} p={p} />)}
            <Pagination data={data} onChange={(p) => search(p)} />
          </div>
        )}
      </div>
    </section>
  );
}
