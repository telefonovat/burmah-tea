import { strings } from "../strings";
import type { Lang, Tab } from "../types";

export default function SiteHeader({
  tab,
  lang,
  onSelectTab,
  onSelectLang,
}: {
  tab: Tab;
  lang: Lang;
  onSelectTab: (t: Tab) => void;
  onSelectLang: (l: Lang) => void;
}) {
  return (
    <header>
      <div className="container">
        <div className="header-row">
          <div>
            <h1>
              Burmahtea<span className="dot">.</span>com
            </h1>
            <p className="tagline">{strings.tagline[lang]}</p>
          </div>
          <button
            className="lang-toggle"
            onClick={() => onSelectLang(lang === "mm" ? "en" : "mm")}
            aria-label="Switch language"
          >
            {lang === "mm" ? "EN" : "MM"}
          </button>
        </div>
        <nav className="tabs">
          <button
            className={tab === "digest" ? "active" : ""}
            onClick={() => onSelectTab("digest")}
          >
            {strings.tabDigest[lang]}
          </button>
          <button
            className={tab === "chat" ? "active" : ""}
            onClick={() => onSelectTab("chat")}
          >
            {strings.tabChat[lang]}
          </button>
        </nav>
      </div>
    </header>
  );
}
