import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Trading bot · strategie',
  description: 'Come stanno andando le strategie del bot di trading crypto: paper, conto demo di Binance e conto vero (spento).',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

/** Il tema scuro, se scelto su questo dispositivo, prima del primo disegno (niente lampo bianco); il chiaro resta quello di sempre. */
const TEMA = `try{if(localStorage.getItem('tema')==='scuro')document.documentElement.dataset.theme='dark'}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: TEMA }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
