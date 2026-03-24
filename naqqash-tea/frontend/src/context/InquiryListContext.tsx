import { createContext, useContext, useMemo, useState } from 'react';
export interface InquiryItem { slug: string; name: string; pricePerKg: number }
const Ctx = createContext<any>(null);
export function InquiryListProvider({ children }: { children: React.ReactNode }) {
  const [teas, setTeas] = useState<InquiryItem[]>(JSON.parse(localStorage.getItem('naqqash-inquiry-list') || '[]'));
  const api = useMemo(() => ({ teas, addTea: (tea: InquiryItem) => { const n = teas.find((t) => t.slug === tea.slug) ? teas : [...teas, tea]; setTeas(n); localStorage.setItem('naqqash-inquiry-list', JSON.stringify(n)); }, removeTea: (slug: string) => { const n = teas.filter((t) => t.slug !== slug); setTeas(n); localStorage.setItem('naqqash-inquiry-list', JSON.stringify(n)); }, clearList: () => { setTeas([]); localStorage.setItem('naqqash-inquiry-list', '[]'); } }), [teas]);
  return <Ctx.Provider value={api}>{children}</Ctx.Provider>;
}
export const useInquiryList = () => useContext(Ctx);
