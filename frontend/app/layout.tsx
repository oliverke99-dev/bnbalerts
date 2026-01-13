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
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="format-detection" content="telephone=no" />
      </head>
      <body className="antialiased bg-slate-950 text-white overflow-x-hidden">
        <NextTopLoader color="#9333ea" showSpinner={false} />
        {children}
        <Toaster position="top-center" theme="dark" />
      </body>
    </html>
  );
}
