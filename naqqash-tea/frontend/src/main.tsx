import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import RootLayout from './layouts/RootLayout';
import { InquiryListProvider } from './context/InquiryListContext';
import './index.css';
import HomePage from './pages/HomePage';
import CollectionPage from './pages/CollectionPage';
import TeaDetailPage from './pages/TeaDetailPage';
import OriginPage from './pages/OriginPage';
import RitualPage from './pages/RitualPage';
import TasterBoxPage from './pages/TasterBoxPage';
import AllocatePage from './pages/AllocatePage';
import BookMeetingPage from './pages/BookMeetingPage';
import WholesalePage from './pages/WholesalePage';
import JournalPage from './pages/JournalPage';
import JournalPostPage from './pages/JournalPostPage';
import GiftSetsPage from './pages/GiftSetsPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import FAQPage from './pages/FAQPage';
import ShippingPage from './pages/ShippingPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import NotFoundPage from './pages/NotFoundPage';
const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 5 * 60 * 1000, retry: 2 } } });
const router = createBrowserRouter([{ element: <RootLayout />, children: [
  { path: '/', element: <HomePage /> }, { path: '/collection', element: <CollectionPage /> }, { path: '/tea/:slug', element: <TeaDetailPage /> },
  { path: '/origin', element: <OriginPage /> }, { path: '/ritual', element: <RitualPage /> }, { path: '/taster-box', element: <TasterBoxPage /> },
  { path: '/allocate', element: <AllocatePage /> }, { path: '/book-meeting', element: <BookMeetingPage /> }, { path: '/wholesale', element: <WholesalePage /> },
  { path: '/journal', element: <JournalPage /> }, { path: '/journal/:slug', element: <JournalPostPage /> }, { path: '/gifts', element: <GiftSetsPage /> },
  { path: '/about', element: <AboutPage /> }, { path: '/contact', element: <ContactPage /> }, { path: '/faq', element: <FAQPage /> },
  { path: '/shipping', element: <ShippingPage /> }, { path: '/privacy', element: <PrivacyPage /> }, { path: '/terms', element: <TermsPage /> }, { path: '*', element: <NotFoundPage /> },
]}]);
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><HelmetProvider><QueryClientProvider client={queryClient}><InquiryListProvider><RouterProvider router={router} /></InquiryListProvider></QueryClientProvider></HelmetProvider></React.StrictMode>);
