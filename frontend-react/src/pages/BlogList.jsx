// BlogList.jsx: danh sách bài viết (3 bài / trang)
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import { dateTimeText } from '../format';
import Pagination from '../components/Pagination';

export default function BlogList() {
  const [params, setParams] = useSearchParams();
  const page = params.get('page') || '1';
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/blogs/', { params: { page } }).then(setData).catch((e) => setError(e.message));
  }, [page]);

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-9 col-sm-offset-1">
            <div className="blog-post-area">
              <h2 className="title text-center">Bài viết mới nhất</h2>
              {error && <div className="alert alert-danger">{error}</div>}
              {data && data.results.length === 0 && <p className="text-center">Chưa có bài viết nào.</p>}
              {data && data.results.map((b) => (
                <div className="single-blog-post" key={b.id}>
                  <h3>{b.title}</h3>
                  <div className="post-meta">
                    <ul>
                      <li><i className="fa fa-user"></i> {b.author || 'Admin'}</li>
                      <li><i className="fa fa-clock-o"></i> {dateTimeText(b.created_at)}</li>
                    </ul>
                  </div>
                  {b.image && <Link to={'/blog/' + b.slug}><img src={b.image} alt={b.title} style={{ maxWidth: '100%' }} /></Link>}
                  <p style={{ marginTop: 15 }}>{b.description}</p>
                  <Link className="btn btn-primary" to={'/blog/' + b.slug}>Đọc tiếp</Link>
                </div>
              ))}
              <Pagination data={data} onChange={(p) => setParams({ page: p })} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
