import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FPOLink TN — உழவர் உற்பத்தியாளர் தளம்",
  description: "FPO Digital Operating System for Tamil Nadu (Erode)",
  manifest: "/manifest.json",
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  themeColor: "#16a34a",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ta">
      <body className="min-h-screen bg-gray-50 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
