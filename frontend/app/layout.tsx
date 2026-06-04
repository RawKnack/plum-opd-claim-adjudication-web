import type { Metadata } from "next";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Plum OPD Claims",
  description: "OPD claim submission and adjudication",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <header className="header">
            <a href="/">Plum OPD Claims</a>
          </header>
          <main className="main">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
