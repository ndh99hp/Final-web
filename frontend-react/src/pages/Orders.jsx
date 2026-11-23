// Orders.jsx: lịch sử mua hàng của member
import { useEffect, useState } from 'react';
import { api } from '../api';
import { dateTimeText, money } from '../format';
import AccountSidebar from '../components/AccountSidebar';
import Pagination from '../components/Pagination';

export default function Orders() {
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/orders/', { params: { page } }).then(setData).catch((e) => setError(e.message));
  }, [page]);

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3"><AccountSidebar /></div>
          <div className="col-sm-9">
            <h2 className="title text-center">Lịch sử mua hàng</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {data && data.results.length === 0 && <p className="text-center">Bạn chưa có đơn hàng nào.</p>}
            {data && data.results.length > 0 && (
              <table className="table table-bordered">
                <thead><tr><th>Mã</th><th>Ngày</th><th>Sản phẩm</th><th>Tổng tiền</th></tr></thead>
                <tbody>
                  {data.results.map((o) => (
                    <tr key={o.id}>
                      <td>#{o.id}</td>
                      <td>{dateTimeText(o.created_at)}</td>
                      <td style={{ whiteSpace: 'pre-line' }}>{o.items}</td>
                      <td>${money(o.price)}</td>
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
