import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Atlas Studio",
  description: "Query editor and dashboard for Atlas",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
