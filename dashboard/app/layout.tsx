import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Trading bot · controllo',
  description: 'Il controllo orario del bot di trading crypto (paper): e\' rotto? perde? cosa e\' cambiato.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body>{children}</body>
    </html>
  );
}
