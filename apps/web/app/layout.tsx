import type { ReactNode } from "react";

export const metadata = {
  title: "자산도우미",
  description: "내 소비가 키우는 또 하나의 나",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          background: "linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)",
          color: "#0f172a",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        {children}
      </body>
    </html>
  );
}
