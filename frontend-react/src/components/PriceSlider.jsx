// PriceSlider.jsx: thanh kéo khoảng giá 2 đầu. Kéo xong (thả chuột / buông phím) thì gọi onCommit([thấp, cao])
import { useEffect, useState } from 'react';

export default function PriceSlider({ max, low, high, onCommit }) {
  const [range, setRange] = useState([low, high]);

  // khi điều kiện lọc thay đổi từ bên ngoài (ví dụ bấm "Xóa bộ lọc") thì cập nhật lại
  useEffect(() => {
    setRange([low, high]);
  }, [low, high, max]);

  const percent = (v) => (max > 0 ? (v / max) * 100 : 0);

  function changeLow(e) {
    setRange([Math.min(Number(e.target.value), range[1]), range[1]]);
  }
  function changeHigh(e) {
    setRange([range[0], Math.max(Number(e.target.value), range[0])]);
  }
  function commit() {
    onCommit(range);
  }

  return (
    <div className="price-range">
      <h2>Khoảng giá</h2>
      <div className="well">
        <div className="range-wrap">
          <div className="range-track"></div>
          <div className="range-fill" style={{ left: percent(range[0]) + '%', right: 100 - percent(range[1]) + '%' }}></div>
          <input type="range" id="range-low" min="0" max={max} step="1" value={range[0]}
            onChange={changeLow} onMouseUp={commit} onTouchEnd={commit} onKeyUp={commit} />
          <input type="range" id="range-high" min="0" max={max} step="1" value={range[1]}
            onChange={changeHigh} onMouseUp={commit} onTouchEnd={commit} onKeyUp={commit} />
        </div>
        <b>$ <span id="price-low">{range[0]}</span></b> <b className="pull-right">$ <span id="price-high">{range[1]}</span></b>
      </div>
    </div>
  );
}
