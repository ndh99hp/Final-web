// ProductForm.jsx: form thêm / sửa sản phẩm (dùng cho member và admin)
// props: product (có thì là sửa), admin (true = admin sửa), onDone(message) gọi khi lưu xong
import { useEffect, useState } from 'react';
import { api, mediaName } from '../api';
import Notice from './Notice';

const MAX_IMAGES = 3;

export default function ProductForm({ product, admin, onDone }) {
  const editing = !!product;
  const [filters, setFilters] = useState(null);
  const [form, setForm] = useState({
    title: product ? product.title : '',
    price: product ? String(product.price) : '',
    status: product ? String(product.status) : '0',
    sale: product && product.status === 1 ? String(product.sale) : '',
    category: product && product.category ? String(product.category) : '',
    brand: product && product.brand ? String(product.brand) : '',
    company: product ? product.company : '',
    detail: product ? product.detail : '',
  });
  const [deleteImages, setDeleteImages] = useState([]); // tên các hình cũ bị tick xóa
  const [files, setFiles] = useState([]);                // hình mới chọn
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api('/filters/').then(setFilters).catch(() => {});
  }, []);

  function setField(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function toggleDelete(name) {
    if (deleteImages.includes(name)) setDeleteImages(deleteImages.filter((n) => n !== name));
    else setDeleteImages([...deleteImages, name]);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    // kiểm tra số hình trước khi gửi (server cũng kiểm tra lại)
    const oldCount = editing ? product.images.length - deleteImages.length : 0;
    if (oldCount + files.length > MAX_IMAGES) {
      setError('Tổng số hình không được quá ' + MAX_IMAGES);
      return;
    }

    // có file nên gửi bằng FormData
    const data = new FormData();
    Object.keys(form).forEach((key) => data.append(key, form[key]));
    deleteImages.forEach((name) => data.append('delete_images', name));
    files.forEach((f) => data.append('images', f));

    setSaving(true);
    try {
      if (editing) {
        const url = admin ? '/admin/products/update/' : '/my-products/update/';
        await api(url + product.id + '/', { method: 'PUT', body: data });
        onDone('Đã cập nhật sản phẩm "' + form.title + '" thành công');
      } else {
        await api('/my-products/create/', { method: 'POST', body: data });
        onDone('Đã thêm sản phẩm "' + form.title + '" thành công');
      }
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  const cats = filters ? filters.categories : [];
  const brands = filters ? filters.brands : [];

  return (
    <form onSubmit={handleSubmit} className="box">
      <Notice>{error}</Notice>

      <label>Tên sản phẩm *</label>
      <input type="text" name="title" className="form-control" value={form.title} onChange={setField} maxLength="255" required style={{ marginBottom: 15 }} />

      <label>Giá gốc ($) *</label>
      <input type="number" step="0.01" min="0" name="price" className="form-control" value={form.price} onChange={setField} required style={{ marginBottom: 15 }} />

      <div className="row">
        <div className="col-sm-6">
          <label>Danh mục</label>
          <select name="category" className="form-control" value={form.category} onChange={setField} style={{ marginBottom: 15 }}>
            <option value="">------</option>
            {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="col-sm-6">
          <label>Thương hiệu</label>
          <select name="brand" className="form-control" value={form.brand} onChange={setField} style={{ marginBottom: 15 }}>
            <option value="">------</option>
            {brands.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      </div>

      <label>Trạng thái</label>
      <select name="status" className="form-control" value={form.status} onChange={setField} style={{ marginBottom: 15 }}>
        <option value="0">New (hàng mới)</option>
        <option value="1">Sale (giảm giá)</option>
      </select>

      {form.status === '1' && (
        <>
          <label>Giá sale ($) * <small className="text-muted">(nhỏ hơn giá gốc)</small></label>
          <input type="number" step="0.01" min="0" name="sale" className="form-control" value={form.sale} onChange={setField} style={{ marginBottom: 15 }} />
        </>
      )}

      <label>Công ty</label>
      <input type="text" name="company" className="form-control" value={form.company} onChange={setField} maxLength="255" style={{ marginBottom: 15 }} />

      <label>Mô tả chi tiết</label>
      <textarea name="detail" rows="5" className="form-control" value={form.detail} onChange={setField} style={{ marginBottom: 15 }}></textarea>

      {editing && product.images.length > 0 && (
        <div style={{ marginBottom: 15 }}>
          <label>Hình hiện tại <small className="text-muted">(tick để xóa)</small></label>
          <div>
            {product.images.map((url) => {
              const name = mediaName(url);
              return (
                <label key={url} style={{ marginRight: 15, fontWeight: 'normal', textAlign: 'center' }}>
                  <img src={url} alt="" style={{ width: 90, height: 90, objectFit: 'cover', display: 'block', opacity: deleteImages.includes(name) ? 0.35 : 1 }} />
                  <input type="checkbox" checked={deleteImages.includes(name)} onChange={() => toggleDelete(name)} /> Xóa
                </label>
              );
            })}
          </div>
        </div>
      )}

      <label>Thêm hình <small className="text-muted">(tối đa {MAX_IMAGES} hình, mỗi hình dưới 1MB)</small></label>
      <input type="file" accept="image/*" multiple onChange={(e) => setFiles(Array.from(e.target.files))} style={{ marginBottom: 20 }} />

      <button type="submit" className="btn btn-primary" disabled={saving}>{editing ? 'Lưu thay đổi' : 'Thêm sản phẩm'}</button>
    </form>
  );
}
