// NotFound.jsx: trang 404
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="container text-center">
      <div className="content-404">
        <img src="/images/404/404.png" className="img-responsive" alt="" style={{ margin: '0 auto' }} />
        <h1><b>OPPS!</b> Không tìm thấy trang</h1>
        <p>Trang bạn tìm không tồn tại.</p>
        <h2><Link to="/">Về trang chủ</Link></h2>
      </div>
    </div>
  );
}
