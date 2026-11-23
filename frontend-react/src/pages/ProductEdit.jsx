// ProductEdit.jsx: thêm / sửa sản phẩm. Dùng chung cho member (/account/...) và admin (/admin/products/:id/edit)
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import AccountSidebar from '../components/AccountSidebar';
import AdminSidebar from '../components/AdminSidebar';
import ProductForm from '../components/ProductForm';

export default function ProductEdit({ admin }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState('');

  // có id thì lấy sản phẩm cũ để sửa
  useEffect(() => {
    if (!id) return;
    api('/products/' + id + '/').then((d) => setProduct(d.product)).catch((e) => setError(e.message));
  }, [id]);

  function done(message) {
    navigate(admin ? '/admin/products' : '/account/my-product', { state: { message } });
  }

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-3">{admin ? <AdminSidebar /> : <AccountSidebar />}</div>
          <div className="col-sm-9">
            <h2 className="title text-center">{id ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}</h2>
            {error && <div className="alert alert-danger">{error}</div>}
            {(!id || product) && <ProductForm product={product} admin={admin} onDone={done} />}
          </div>
        </div>
      </div>
    </section>
  );
}
