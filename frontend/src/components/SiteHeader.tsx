import { Link } from "react-router-dom";

export default function SiteHeader() {
  return (
    <header>
      <div className="container">
        <h1>
          Burmahtea<span className="dot">.</span>com
        </h1>
        <p className="tagline">မြန်မာ ဖေ့စ်ဘွတ်ခ်မှ နောက်ဆုံး သတင်းများ</p>
        <nav className="site-nav">
          <Link to="/">ဒိုင်းဂျက်</Link>
          <Link to="/chat">💬 မေးမြန်း</Link>
        </nav>
      </div>
    </header>
  );
}
