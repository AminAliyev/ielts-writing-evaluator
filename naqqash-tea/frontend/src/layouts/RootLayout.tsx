import { Outlet, Link } from 'react-router-dom';
import { useInquiryList } from '../context/InquiryListContext';
export default function RootLayout() { const { teas } = useInquiryList(); return <div><header className='sticky top-0 bg-white/90 p-4 flex gap-4'><Link to='/'>Naqqash Tea</Link><Link to='/collection'>Collection</Link><Link to='/taster-box'>Taster Box</Link><Link to='/allocate'>Allocate</Link><div className='ml-auto'>Inquiry {teas.length}</div></header><main><Outlet/></main><footer className='bg-[#2D4A37] text-white p-8 mt-12'>© Naqqash Tea</footer></div>; }
