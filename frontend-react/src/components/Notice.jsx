// Notice.jsx: khung thông báo (xanh = thành công, đỏ = lỗi). Không có nội dung thì không hiện gì
export default function Notice({ type = 'danger', children }) {
  if (!children) return null;
  return <div className={'alert alert-' + type}>{children}</div>;
}
