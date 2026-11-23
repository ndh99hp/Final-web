// MyProducts.jsx: danh sách sản phẩm của tôi (tìm theo tên, sửa, xóa)
import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { api } from '../api';
import { DEFAULT_IMAGE, money } from '../format';
import AccountSidebar from '../components/AccountSidebar';
import Notice from '../components/Notice';
import Pagination from '../components/Pagination';

export default function MyProducts() {
  const location = useLocation();
  const [q, setQ] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState((location.state && location.state.message) || '');

  function load() {
    api('/my-products/', { params: { q: search, page } }).then(setData).catch((e) => setError(e.message));
  }
  useEffect(load, [search, page]);

  async function handleDelete(p) {
    if (!window.confirm('Xóa sản phẩm "' + p.title + '"?')) return;
    try {
      await api('/my-products/delete/' + p.id + '/', { method: 'DELETE' });
      setMessage('Đã xóa sản phẩm "' + p.title + '"');
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AccountSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Sản phẩm của tôi</h2>
            <Notice type="success">{message}</Notice>
            <Notice>{error}</Notice>
            <form className="form-inline" style={{ marginBottom: 15 }} onSubmit={(e) => { e.preventDefault(); setPage(1); setSearch(q); }}>
              <input type="text" className="form-control" placeholder="Tìm theo tên" value={q} onChange={(e) => setQ(e.target.value)} />{' '}
              <button className="btn btn-default">Tìm</button>{' '}
              <Link to="/account/add-product" className="btn btn-primary pull-right">+ Thêm sản phẩm</Link>
            </form>
            {data && data.results.length === 0 && <p className="text-center">Chưa có sản phẩm nào.</p>}
            {data && data.results.length > 0 && (
              <table className="table table-bordered">
                <thead><tr><th>ID</th><th>Hình</th><th>Tên</th><th>Giá</th><th>Trạng thái</th><th></th></tr></thead>
                <tbody>
                  {data.results.map((p) => (
                    <tr key={p.id}>
                      <td>{p.id}</td>
                      <td><img src={p.image || DEFAULT_IMAGE} alt="" style={{ width: 60, height: 60, objectFit: 'cover' }} /></td>
                      <td><Link to={'/shop/' + p.id}>{p.title}</Link></td>
                      <td>{p.status === 1 ? <><b>${money(p.sale)}</b> <del>${money(p.price)}</del></> : '$' + money(p.price)}</td>
                      <td>{p.status === 1 ? 'Sale' : 'New'}</td>
                      <td>
                        <Link to={'/account/edit-product/' + p.id} className="btn btn-xs btn-default">Sửa</Link>{' '}
                        <button className="btn btn-xs btn-danger" onClick={() => handleDelete(p)}>Xóa</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <Pagination data={data} onChange={setPage} />
          </div>
        </div>
      </div>
    </section>
  );
}
