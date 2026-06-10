import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Trading Bot Dashboard',
  description: 'Live dashboard for the agentic crypto futures trading bot',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
