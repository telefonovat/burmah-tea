// UI strings per language. Burmese-first; English is the toggle.
import type { Lang } from "./types";

type Str = Record<Lang, string>;

export const strings: {
  tagline: Str;
  tabDigest: Str;
  tabChat: Str;
  sectionTea: Str;
  sectionNews: Str;
  shuffle: Str;
  digestError: Str;
  chatHint: Str;
  chatError: Str;
  retry: Str;
  newChat: Str;
  chipNews: Str;
  chipTea: Str;
  inputPlaceholder: Str;
  sources: Str;
  footer: Str;
} = {
  tagline: {
    mm: "မြန်မာ ဖေ့စ်ဘွတ်ခ်မှ နောက်ဆုံး သတင်းများ",
    en: "Latest news from Myanmar's Facebook",
  },
  tabDigest: { mm: "ဒိုင်းဂျက်", en: "Digest" },
  tabChat: { mm: "စကားပြော", en: "Chat" },
  sectionTea: { mm: "လက်ဖက်ရည်", en: "Tea" },
  sectionNews: { mm: "သတင်း", en: "News" },
  shuffle: { mm: "အသစ်ရွှေ့", en: "Shuffle" },
  digestError: {
    mm: "ဒိုင်းဂျက် မရရှိပါ။ Backend လည်ပတ်နေပါသလား?",
    en: "No digest yet. Is the backend running?",
  },
  chatHint: {
    mm: "ဒီနေ့ ဒိုင်းဂျက်အကြောင်း မေးမြန်းနိုင်ပါသည်။",
    en: "Ask anything about today's digest.",
  },
  chatError: {
    mm: "ချိတ်ဆက်မှု မအောင်မြင်ပါ။ Backend လည်ပတ်နေပါသလား?",
    en: "Connection failed. Is the backend running?",
  },
  retry: { mm: "ထပ်စမ်းကြည့်", en: "Retry" },
  newChat: { mm: "ချက် အသစ်ဖွင့်ရန်", en: "New chat" },
  chipNews: { mm: "ဒီနေ့ ဘာသတင်းတွေရှိလဲ", en: "What's the news today?" },
  chipTea: { mm: "ဒီနေ့ အတင်း ဘာတွေလဲ", en: "What's the tea today?" },
  inputPlaceholder: {
    mm: "မေးခွန်း ရေးပါ… (Shift+Enter = စာလုံးအသစ်)",
    en: "Ask a question… (Shift+Enter for a new line)",
  },
  sources: { mm: "ရင်းမြစ်", en: "Sources" },
  footer: {
    mm: "Burmahtea.com – မြန်မာ ဖေ့စ်ဘွတ်ခ် နေ့စဉ် ဒိုင်းဂျက်။",
    en: "Burmahtea.com – Myanmar's daily Facebook digest.",
  },
};

export function dateLabel(date: string, lang: Lang): string {
  const locale = lang === "mm" ? "my-MM" : "en-US";
  // digest.date is a Myanmar-calendar day; anchor to MMT midnight.
  const d = new Date(`${date}T00:00:00+06:30`);
  return d.toLocaleDateString(locale, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export const TAG_LABEL: Record<string, Str> = {
  confirmed: { mm: "အတည်ပြု", en: "confirmed" },
  popular: { mm: "လူကြိုက်များ", en: "popular" },
  tea: { mm: "အတင်း", en: "tea" },
};

export const TIER_LABEL: Record<string, Str> = {
  trustworthy: { mm: "ယုံကြည်ရ", en: "trustworthy" },
  subpar: { mm: "အလယ်အလတ်", en: "mixed" },
  tabloid: { mm: "တက်ဘွိုက်", en: "tabloid" },
  celebrity: { mm: "ပုဂ္ဂလိက", en: "personal" },
};

const MM_DIGITS = "၀၁၂၃၄၅၆၇၈၉";

/** Local digits: Burmese numerals in Burmese mode, Latin otherwise. */
export function num(n: number | string, lang: Lang): string {
  const s = String(n);
  return lang === "mm" ? s.replace(/[0-9]/g, (d) => MM_DIGITS[Number(d)]) : s;
}

export const sectionCount: Str = { mm: "ပုဒ်", en: "shown" };
