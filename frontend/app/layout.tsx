import type { Metadata } from "next";
import "./globals.css";
import ClientRoot from "@/components/ClientRoot";

const geistSans = {
  variable: "--font-geist-sans"
};
const geistMono = {
  variable: "--font-geist-mono"
};

export const metadata: Metadata = {
  title: "Email Agent - Smart Email Management",
  description: "AI-powered email management and organization",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="antialiased min-h-screen bg-background text-foreground">
        <ClientRoot>{children}</ClientRoot>
      </body>
    </html>
  );
}
