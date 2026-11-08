import { useState } from "react";
import SiteHeader from "./components/SiteHeader";
import DigestView from "./components/DigestView";
import ChatView from "./components/ChatView";
import { strings } from "./strings";
import type { Lang, Tab } from "./types";

export default function App() {
  const [tab, setTab] = useState<Tab>("digest");
  const [lang, setLang] = useState<Lang>("mm");

  return (
    <div className="app">
      <SiteHeader tab={tab} lang={lang} onSelectTab={setTab} onSelectLang={setLang} />
      <div className="container">
        {tab === "digest" ? <DigestView lang={lang} /> : <ChatView lang={lang} />}
      </div>
      <footer>
        <div className="container">
          <p>{strings.footer[lang]}</p>
        </div>
      </footer>
    </div>
  );
}
