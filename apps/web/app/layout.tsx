import type { ReactNode } from "react";
import { IBM_Plex_Sans_KR } from "next/font/google";

const ibmPlexSansKr = IBM_Plex_Sans_KR({
  subsets: ["latin", "latin-ext"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata = {
  title: "자산도우미",
  description: "내 소비가 키우는 또 하나의 나",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ko">
      <body
        className={ibmPlexSansKr.className}
        style={{
          margin: 0,
          minHeight: "100vh",
          background:
            "radial-gradient(circle at 12% 10%, rgba(59,130,246,0.18), transparent 26%), radial-gradient(circle at 88% 14%, rgba(6,182,212,0.16), transparent 22%), radial-gradient(circle at 50% 100%, rgba(99,102,241,0.10), transparent 30%), linear-gradient(180deg, #fbfdff 0%, #eef4ff 48%, #eaf2ff 100%)",
          color: "#0f172a",
        }}
      >
        {children}
      </body>
    </html>
  );
}
