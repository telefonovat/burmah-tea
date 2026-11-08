import { useEffect, useState } from "react";
import type { Digest } from "../types";

type DigestState =
  | { status: "loading" }
  | { status: "error" }
  | { status: "ready"; digest: Digest };

export function useDigest() {
  const [state, setState] = useState<DigestState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setState({ status: "loading" });
      try {
        const res = await fetch("/api/digest/today");
        if (!res.ok) throw new Error(String(res.status));
        const digest: Digest = await res.json();
        if (!cancelled) setState({ status: "ready", digest });
      } catch {
        if (!cancelled) setState({ status: "error" });
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
