// Pagination.jsx: phân trang. data = { page, total_pages } lấy từ API
export default function Pagination({ data, onChange }) {
  if (!data || data.total_pages <= 1) return null;
  const pages = [];
  for (let i = 1; i <= data.total_pages; i++) pages.push(i);
  return (
    <div className="col-sm-12 text-center">
      <ul className="pagination">
        {data.page > 1 && <li><a onClick={() => onChange(data.page - 1)}>&laquo;</a></li>}
        {pages.map((p) => (
          <li key={p} className={p === data.page ? 'active' : ''}>
            <a onClick={() => onChange(p)}>{p}</a>
          </li>
        ))}
        {data.page < data.total_pages && <li><a onClick={() => onChange(data.page + 1)}>&raquo;</a></li>}
      </ul>
    </div>
  );
}
