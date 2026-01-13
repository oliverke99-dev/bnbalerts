"use client";

import React from 'react';
import { Toaster } from 'sonner';
import NextTopLoader from "nextjs-toploader";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-950 text-white">
        <NextTopLoader color="#9333ea" showSpinner={false} />
        {children}
        <Toaster position="top-center" theme="dark" />
      </body>
    </html>
  );
}
