import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SQX Edge Tester Portal",
  description: "Controlled tester portal bootstrap for SQX Edge Pro.",
  robots: {
    index: false,
    follow: false
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

