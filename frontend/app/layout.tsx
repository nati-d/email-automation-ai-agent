import type { Metadata, Viewport } from "next";
import { Nunito } from "next/font/google";
import "./globals.css";
import ClientRoot from "@/components/ClientRoot";

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-nunito",
  weight: ["200", "300", "400", "500", "600", "700", "800", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "EmailAI - Smart Email Management",
  description: "AI-powered email management and organization with intelligent categorization, task extraction, and automated responses",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={nunito.variable}>
      <body className="antialiased min-h-screen bg-background text-foreground font-sans">
        <ClientRoot>{children}</ClientRoot>
      </body>
    </html>
  );
}
