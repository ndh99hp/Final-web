// Sidebar.jsx: thanh bên trái: Danh mục + Thương hiệu (dữ liệu lấy từ api /filters/)
export default function Sidebar({ filters, categoryId, brandId, onCategory, onBrand, children }) {
  const orange = { color: '#fe980f' };
  const cats = filters ? filters.categories : [];
  const brands = filters ? filters.brands : [];
  return (
    <div className="left-sidebar">
      <h2>Danh mục</h2>
      <div className="panel-group category-products">
        <div className="panel panel-default">
          <div className="panel-heading">
            <h4 className="panel-title">
              <a className="cursor" style={!categoryId ? orange : null} onClick={() => onCategory('')}>Tất cả danh mục</a>
            </h4>
          </div>
        </div>
        {cats.map((c) => (
          <div className="panel panel-default" key={c.id}>
            <div className="panel-heading">
              <h4 className="panel-title">
                <a className="cursor" style={String(categoryId) === String(c.id) ? orange : null} onClick={() => onCategory(c.id)}>
                  <span className="badge pull-right">{c.total}</span>{c.name}
                </a>
              </h4>
            </div>
          </div>
        ))}
      </div>

      <div className="brands_products">
        <h2>Thương hiệu</h2>
        <div className="brands-name">
          <ul className="nav nav-pills nav-stacked">
            <li><a className="cursor" style={!brandId ? orange : null} onClick={() => onBrand('')}>Tất cả thương hiệu</a></li>
            {brands.map((b) => (
              <li key={b.id}>
                <a className="cursor" style={String(brandId) === String(b.id) ? orange : null} onClick={() => onBrand(b.id)}>
                  <span className="pull-right">({b.total})</span>{b.name}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
      {children}
    </div>
  );
}
