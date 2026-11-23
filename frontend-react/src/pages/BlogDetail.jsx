// BlogDetail.jsx: chi tiết bài viết + đánh giá sao + bình luận lồng nhau
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../auth';
import { dateTimeText } from '../format';
import Notice from '../components/Notice';

// 1 bình luận + các bình luận trả lời nó (gọi lại chính nó cho các cấp con)
function CommentNode({ c, user, onReply }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  async function send(e) {
    e.preventDefault();
    try {
      await onReply(text, c.id);
      setText('');
      setOpen(false);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <li className={c.level > 0 ? 'media second-media' : 'media'} style={{ listStyle: 'none', marginTop: 20 }}>
        <div className="media-body" style={{ marginLeft: c.level > 0 ? 50 : 0 }}>
          <ul className="sinlge-post-meta" style={{ paddingLeft: 0 }}>
            <li><i className="fa fa-user"></i> {c.name}</li>
            <li><i className="fa fa-clock-o"></i> {dateTimeText(c.created_at)}</li>
          </ul>
          <p style={{ whiteSpace: 'pre-line' }}>{c.cmt}</p>
          {user && <a className="btn btn-primary cursor" onClick={() => setOpen(!open)}><i className="fa fa-reply"></i> Trả lời</a>}
          {open && (
            <form onSubmit={send} style={{ marginTop: 10 }}>
              <Notice>{error}</Notice>
              <textarea className="form-control" rows="3" value={text} onChange={(e) => setText(e.target.value)} placeholder="Nhập câu trả lời..." required></textarea>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 8 }}>Gửi</button>
            </form>
          )}
        </div>
      </li>
      {c.replies.map((r) => <CommentNode key={r.id} c={r} user={user} onReply={onReply} />)}
    </>
  );
}

export default function BlogDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [hover, setHover] = useState(0);
  const [rateMsg, setRateMsg] = useState('');
  const [cmt, setCmt] = useState('');
  const [cmtError, setCmtError] = useState('');

  async function load() {
    try {
      setData(await api('/blogs/' + slug + '/'));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => { setData(null); load(); }, [slug, user]);

  if (error) return <section><div className="container"><div className="alert alert-danger">{error}</div><Link to="/blog">Về danh sách blog</Link></div></section>;
  if (!data) return <section><div className="container"><p>Đang tải...</p></div></section>;

  const { blog, comments, prev, next, rating } = data;

  async function rate(value) {
    if (!user) { setRateMsg('Vui lòng đăng nhập để đánh giá'); return; }
    try {
      await api('/blogs/' + slug + '/rate/', { method: 'POST', body: { rate: value } });
      setRateMsg('Cảm ơn bạn đã đánh giá!');
      load();
    } catch (e) {
      setRateMsg(e.message);
    }
  }

  // gửi bình luận (parentId rỗng = bình luận mới, có = trả lời)
  async function sendComment(text, parentId) {
    await api('/blogs/' + slug + '/comment/', { method: 'POST', body: { cmt: text, parent_id: parentId || null } });
    await load();
  }

  async function handleNewComment(e) {
    e.preventDefault();
    try {
      await sendComment(cmt, null);
      setCmt('');
      setCmtError('');
    } catch (err) {
      setCmtError(err.message);
    }
  }

  // sao hiển thị: đang rê chuột > điểm của mình > điểm trung bình
  const shown = hover || rating.your_rate || rating.average;

  return (
    <section>
      <div className="container">
        <div className="row">
          <div className="col-sm-9 col-sm-offset-1">
            <div className="blog-post-area">
              <h2 className="title text-center">{blog.title}</h2>
              <div className="single-blog-post">
                <div className="post-meta">
                  <ul>
                    <li><i className="fa fa-user"></i> {blog.author || 'Admin'}</li>
                    <li><i className="fa fa-clock-o"></i> {dateTimeText(blog.created_at)}</li>
                  </ul>
                </div>
                {blog.image && <img src={blog.image} alt={blog.title} style={{ maxWidth: '100%' }} />}
                <p style={{ marginTop: 15, fontWeight: 'bold' }}>{blog.description}</p>
                <div dangerouslySetInnerHTML={{ __html: blog.content }} />
              </div>
            </div>

            <div className="rating-area">
              <p>
                <b>Đánh giá:</b> {rating.average_raw}/5 ({rating.count} lượt)
                {rating.your_rate ? ' - bạn đã chấm ' + rating.your_rate + ' sao' : ''}
              </p>
              <div className="rate-stars" onMouseLeave={() => setHover(0)} style={{ fontSize: 28, color: '#fe980f', cursor: rating.your_rate ? 'default' : 'pointer' }}>
                {[1, 2, 3, 4, 5].map((n) => (
                  <span key={n}
                    onMouseEnter={() => !rating.your_rate && setHover(n)}
                    onClick={() => !rating.your_rate && rate(n)}>
                    {n <= shown ? '★' : '☆'}
                  </span>
                ))}
              </div>
              {rateMsg && <p className="text-muted">{rateMsg}</p>}
            </div>

            <div className="pager-area" style={{ margin: '20px 0' }}>
              {prev && <Link to={'/blog/' + prev.slug} className="btn btn-default">&laquo; {prev.title}</Link>}{' '}
              {next && <Link to={'/blog/' + next.slug} className="btn btn-default pull-right">{next.title} &raquo;</Link>}
            </div>

            <div className="response-area" style={{ clear: 'both' }}>
              <h2>{comments.length} bình luận</h2>
              <ul className="media-list" style={{ paddingLeft: 0 }}>
                {comments.map((c) => <CommentNode key={c.id} c={c} user={user} onReply={sendComment} />)}
              </ul>
            </div>

            <div className="replay-box" style={{ marginTop: 30 }}>
              <h2>Viết bình luận</h2>
              {user ? (
                <form onSubmit={handleNewComment}>
                  <Notice>{cmtError}</Notice>
                  <textarea className="form-control" rows="5" value={cmt} onChange={(e) => setCmt(e.target.value)} placeholder="Nội dung bình luận..." required></textarea>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: 10 }}>Gửi bình luận</button>
                </form>
              ) : (
                <p>Vui lòng <Link to="/login" state={{ from: '/blog/' + slug }}>đăng nhập</Link> để bình luận và đánh giá.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
