// format.js: các hàm định dạng hiển thị
export const DEFAULT_IMAGE = '/images/home/product1.jpg'; // hình mặc định khi sản phẩm chưa có hình

// 1234.5 -> "1,234.50"
export function money(value) {
  return Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// "2026-10-03T10:29:37Z" -> "03/10/2026"
export function dateText(value) {
  if (!value) return '';
  return new Date(value).toLocaleDateString('vi-VN');
}

// -> "03/10/2026 17:29"
export function dateTimeText(value) {
  if (!value) return '';
  const d = new Date(value);
  return d.toLocaleDateString('vi-VN') + ' ' + d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}
