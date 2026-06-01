import type { ReactNode } from "react";

export const metadata = {
  title: "InvoiceFlow",
  description: "Invoice management SaaS",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

