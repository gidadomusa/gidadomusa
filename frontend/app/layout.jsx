import './globals.css';

export const metadata = {
  title: 'Your App Name',
  description: 'Short description of your app',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>
        <noscript>
          This application requires JavaScript to run. Please enable JavaScript in your browser.
        </noscript>

        <div id="__next" role="main" aria-label="Application root">
          {children}
        </div>
      </body>
    </html>
  );
}
