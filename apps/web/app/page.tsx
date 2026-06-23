"use client";

import { useEffect, useMemo, useState } from "react";

const responsiveStyles = `
  * {
    box-sizing: border-box;
  }

  :root {
    color-scheme: light;
    --bg: #eef4ff;
    --surface: rgba(255, 255, 255, 0.78);
    --surface-strong: rgba(255, 255, 255, 0.92);
    --border: rgba(148, 163, 184, 0.18);
    --text: #0f172a;
    --muted: #64748b;
    --primary: #2563eb;
    --primary-strong: #1d4ed8;
    --accent: #06b6d4;
    --accent-soft: #e0f2fe;
    --shadow: 0 24px 80px rgba(15, 23, 42, 0.10);
  }
  
  body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--text);
  }
  
  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  main::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background:
      radial-gradient(circle at 15% 20%, rgba(37, 99, 235, 0.14), transparent 28%),
      radial-gradient(circle at 85% 12%, rgba(6, 182, 212, 0.14), transparent 24%),
      radial-gradient(circle at 50% 88%, rgba(99, 102, 241, 0.10), transparent 30%);
    z-index: 0;
  }

  main > * {
    position: relative;
    z-index: 1;
  }
  
  section {
    width: 100%;
  }
  
  input, select, textarea {
    font-size: 16px;
    padding: clamp(8px, 2vw, 12px);
    border: 1px solid rgba(148, 163, 184, 0.24);
    background: rgba(255, 255, 255, 0.92);
    color: var(--text);
  }
  
  button {
    font-size: clamp(13px, 2.5vw, 14px);
  }
  
  @media (max-width: 768px) {
    main {
      padding: 32px 16px 140px !important;
    }
    
    h1 {
      font-size: 28px !important;
      line-height: 1.2 !important;
      margin-bottom: 12px !important;
    }
    
    h2 {
      font-size: 20px !important;
    }
    
    p {
      font-size: 14px !important;
    }
    
    section {
      padding: 20px !important;
      border-radius: 16px !important;
    }
    
    label {
      font-size: 13px !important;
    }
  }
  
  @media (max-width: 480px) {
    main {
      padding: 20px 12px 120px !important;
    }
    
    h1 {
      font-size: 22px !important;
      line-height: 1.2 !important;
    }
    
    h2 {
      font-size: 16px !important;
    }
    
    h3 {
      font-size: 15px !important;
    }
    
    p {
      font-size: 13px !important;
      line-height: 1.5 !important;
    }
    
    section {
      padding: 16px !important;
      border-radius: 12px !important;
      margin-bottom: 16px !important;
    }
    
    button {
      font-size: 13px !important;
      padding: 8px 10px !important;
      min-height: 40px !important;
      border-radius: 6px !important;
    }
    
    input, select, textarea {
      font-size: 16px !important;
      padding: 10px 8px !important;
      width: 100% !important;
      border-radius: 6px !important;
    }
    
    label {
      font-size: 12px !important;
      display: block !important;
      margin-bottom: 6px !important;
    }
    
    nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      width: 100%;
      z-index: 999;
    }
  }
`;

type MenuTab = "주식" | "홈" | "미션" | "랭킹";

type StockCompany = {
  symbol: string;
  name: string;
  price: number;
  drift: number;
  volatility: number;
  liquidity: number;
  lastChange: number;
  orderPressure: number;
};

type MissionRankingItem = {
  rank: number;
  user_id: string;
  nickname: string;
  completed_count: number;
};

type MissionMyRank = {
  rank: number;
  user_id: string;
  nickname: string;
  completed_count: number;
};

type BankApiLinkSummary = {
  user_id: string;
  bank_code: string;
  account_number_masked: string;
  linked_at: string;
  last_polled_at: string | null;
};

type BankApiPollResult = {
  user_id: string;
  current_balance: number;
  new_transaction_count: number;
  total_hp_drop: number;
  hp: number;
  polled_at: string;
};

type BankApiBalancePoint = {
  balance: number;
  polled_at: string;
};

type BankApiTransaction = {
  date: string;
  time: string;
  description?: string;
  displayName?: string;
  counterparty?: string;
  amount: number;
  balance: number;
  type: string;
  branch?: string;
  memo?: string;
};

const menuTabs: MenuTab[] = ["주식", "홈", "미션", "랭킹"];

const initialCompanies: StockCompany[] = [
  { symbol: "MTR", name: "메타리테일", price: 48500, drift: 0.08, volatility: 0.9, liquidity: 5200, lastChange: 0, orderPressure: 0 },
  { symbol: "GEX", name: "그린에너지X", price: 73200, drift: 0.11, volatility: 1.3, liquidity: 3300, lastChange: 0, orderPressure: 0 },
  { symbol: "NCS", name: "뉴클라우드솔루션", price: 118000, drift: 0.14, volatility: 1.7, liquidity: 2400, lastChange: 0, orderPressure: 0 },
  { symbol: "HFB", name: "헬스바이오랩", price: 35600, drift: 0.05, volatility: 1.5, liquidity: 4100, lastChange: 0, orderPressure: 0 },
  { symbol: "LGT", name: "로지텍모빌리티", price: 92400, drift: 0.09, volatility: 1.1, liquidity: 2900, lastChange: 0, orderPressure: 0 },
];

const dailyMissionPool = [
  "오늘 로그인 1회 완료",
  "HP 계산 1회 실행",
  "오늘 HP 80 이상 1회 달성",
  "주식 매수 1회 완료",
  "주식 매도 1회 완료",
  "오늘 총 거래 2회 이상 완료",
  "보유 종목 1개 이상 만들기",
  "보유 종목 2개 이상 만들기",
  "총 자산 화면 1회 이상 확인",
  "미션 탭에서 미션 1개 완료",
  "오늘 미션 3개 이상 완료",
  "랭킹 탭 1회 방문",
];

const weeklyMissionPool = [
  "주간 누적 로그인 5일 이상 달성",
  "주간 누적 HP 계산 10회 이상 달성",
  "주간 HP 80 이상 달성일 5일 이상",
  "주간 누적 매수 10회 이상 완료",
  "주간 누적 매도 10회 이상 완료",
  "주간 누적 거래 30회 이상 완료",
  "주간 보유 종목 3개 이상 유지",
  "주간 미션 누적 완료 20개 이상",
  "주간 랭킹 탭 방문 5회 이상",
  "주간 최고 HP 90 이상 3회 달성",
];

const randomMissionPool = [
  "24시간 내 HP 계산 3회 완료",
  "24시간 내 총 거래 5회 완료",
  "24시간 내 매수 3회 완료",
  "24시간 내 매도 3회 완료",
  "24시간 내 미션 2개 완료",
  "24시간 내 랭킹 탭 2회 방문",
  "24시간 내 보유 종목 2개 이상 달성",
  "24시간 내 HP 85 이상 2회 달성",
];

const DAY_MS = 24 * 60 * 60 * 1000;

function toLocalDateKey(date: Date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getWeekStartKey(date: Date) {
  const weekStart = new Date(date);
  const dayOfWeek = weekStart.getDay();
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  weekStart.setDate(weekStart.getDate() + diffToMonday);
  weekStart.setHours(0, 0, 0, 0);
  return toLocalDateKey(weekStart);
}

function hashText(text: string) {
  let hash = 2166136261;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash >>> 0);
}

function pickMissionsBySeed(pool: string[], count: number, seed: string) {
  return [...pool]
    .map((mission, index) => ({
      mission,
      rank: hashText(`${seed}-${index}-${mission}`),
    }))
    .sort((a, b) => a.rank - b.rank)
    .slice(0, count)
    .map((item) => item.mission);
}

function formatKrw(value: number) {
  return `${Math.round(value).toLocaleString("ko-KR")}원`;
}

function resolveOpenBankingUserId(stateParam: string | null, currentUserId: string) {
  if (stateParam) {
    const trimmed = stateParam.trim();
    if (trimmed) {
      try {
        const parsed = JSON.parse(trimmed) as { user_id?: string; userId?: string };
        const fromJson = parsed.user_id || parsed.userId;
        if (typeof fromJson === "string" && fromJson.trim()) {
          return fromJson.trim();
        }
      } catch {
        // state가 단순 문자열인 경우를 허용한다.
      }
      return trimmed;
    }
  }

  return currentUserId.trim();
}

function estimateExecutionPrice(company: StockCompany, qty: number, side: "buy" | "sell") {
  const impactRatio = qty / company.liquidity;
  return Math.max(
    100,
    Math.round(company.price * (1 + (side === "buy" ? 1 : -1) * impactRatio * 0.35)),
  );
}

export default function HomePage() {
  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    (process.env.NODE_ENV === "development"
      ? "http://127.0.0.1:8000"
      : "https://ca-danker-e2-20260601-api.salmonforest-66a190e0.koreacentral.azurecontainerapps.io");

  const [email, setEmail] = useState("demo@example.com");
  const [avatarType, setAvatarType] = useState("plant");
  const [intensity, setIntensity] = useState("1");
  const [textMode, setTextMode] = useState(false);
  const [baseline, setBaseline] = useState("30000");
  const [hp, setHp] = useState(100);
  const [signupUserId, setSignupUserId] = useState("");
  const [signupPassword, setSignupPassword] = useState("");
  const [signupNickname, setSignupNickname] = useState("");
  const [signupMessage, setSignupMessage] = useState("");
  const [loginUserId, setLoginUserId] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginMessage, setLoginMessage] = useState("");
  const [currentUserId, setCurrentUserId] = useState("");
  const [isAuthPanelOpen, setIsAuthPanelOpen] = useState(false);
  const [authView, setAuthView] = useState<"signup" | "login">("signup");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loggedInNickname, setLoggedInNickname] = useState("");
  const [activeTab, setActiveTab] = useState<MenuTab>("홈");

  const [companies, setCompanies] = useState<StockCompany[]>(initialCompanies);
  const [cash, setCash] = useState(1000000);
  const [holdings, setHoldings] = useState<Record<string, number>>({});
  const [tradeQuantity, setTradeQuantity] = useState<Record<string, string>>({});
  const [tradeMessage, setTradeMessage] = useState("");
  const [nowMs, setNowMs] = useState(() => Date.now());
  const [selectedRandomMissions, setSelectedRandomMissions] = useState<string[]>([]);
  const [randomMissionCycleKey, setRandomMissionCycleKey] = useState("random-cycle-default");
  const [missionDone, setMissionDone] = useState<Record<string, boolean>>({});
  const [missionCompleteMessage, setMissionCompleteMessage] = useState("");
  const [missionRanking, setMissionRanking] = useState<MissionRankingItem[]>([]);
  const [missionRankingLoading, setMissionRankingLoading] = useState(false);
  const [myMissionRank, setMyMissionRank] = useState<MissionMyRank | null>(null);
  const [myMissionRankLoading, setMyMissionRankLoading] = useState(false);
  const [bankCode, setBankCode] = useState("NH");
  const [bankAccountNumber, setBankAccountNumber] = useState("");
  const [bankAccountPassword, setBankAccountPassword] = useState("");
  const [bankResidentNumber, setBankResidentNumber] = useState("");
  const [bankLink, setBankLink] = useState<BankApiLinkSummary | null>(null);
  const [bankBalanceHistory, setBankBalanceHistory] = useState<BankApiBalancePoint[]>([]);
  const [bankTransactionHistory, setBankTransactionHistory] = useState<BankApiTransaction[]>([]);
  const [bankCurrentBalance, setBankCurrentBalance] = useState<number | null>(null);
  const [bankStatusMessage, setBankStatusMessage] = useState("");
  const [bankPolling, setBankPolling] = useState(false);
  const [isBankPanelOpen, setIsBankPanelOpen] = useState(false);

  // Restore session from localStorage on mount
  useEffect(() => {
    const storedUserId = window.localStorage.getItem("asset-helper-last-user-id");
    if (storedUserId && storedUserId.trim()) {
      setCurrentUserId(storedUserId.trim());
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    if (!isAuthPanelOpen) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsAuthPanelOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isAuthPanelOpen]);

  useEffect(() => {
    const timer = setInterval(() => {
      setNowMs(Date.now());
    }, 60000);

    return () => clearInterval(timer);
  }, []);

  const nowDate = useMemo(() => new Date(nowMs), [nowMs]);
  const dailyCycleKey = useMemo(() => toLocalDateKey(nowDate), [nowDate]);
  const weeklyCycleKey = useMemo(() => getWeekStartKey(nowDate), [nowDate]);

  const shownDailyMissions = useMemo(
    () => pickMissionsBySeed(dailyMissionPool, 5, `daily-${dailyCycleKey}`),
    [dailyCycleKey],
  );
  const shownWeeklyMissions = useMemo(
    () => pickMissionsBySeed(weeklyMissionPool, 5, `weekly-${weeklyCycleKey}`),
    [weeklyCycleKey],
  );

  useEffect(() => {
    const storageKey = "asset-helper-random-mission-state";
    const updateRandomMissions = () => {
      const storedRaw = window.localStorage.getItem(storageKey);
      const now = Date.now();

      if (storedRaw) {
        try {
          const stored = JSON.parse(storedRaw) as {
            missions: string[];
            nextRefreshAt: number;
            cycleKey: string;
          };

          if (Array.isArray(stored.missions) && stored.missions.length === 2 && now < stored.nextRefreshAt && stored.cycleKey) {
            setSelectedRandomMissions(stored.missions);
            setRandomMissionCycleKey(stored.cycleKey);
            return;
          }
        } catch {
          // ignore broken storage data
        }
      }

      const randomDays = Math.floor(Math.random() * 7) + 1;
      const nextRefreshAt = now + randomDays * DAY_MS;
      const cycleKey = `random-${now}`;
      const missions = pickMissionsBySeed(randomMissionPool, 2, cycleKey);

      const nextState = {
        missions,
        nextRefreshAt,
        cycleKey,
      };

      window.localStorage.setItem(storageKey, JSON.stringify(nextState));
      setSelectedRandomMissions(missions);
      setRandomMissionCycleKey(cycleKey);
    };

    updateRandomMissions();
  }, [nowMs]);

  const missionCards = useMemo(
    () => [
      ...shownDailyMissions.map((text, index) => ({ id: `${dailyCycleKey}-daily-${index}`, text })),
      ...shownWeeklyMissions.map((text, index) => ({ id: `${weeklyCycleKey}-weekly-${index}`, text })),
      ...selectedRandomMissions.map((text, index) => ({ id: `${randomMissionCycleKey}-random-${index}`, text })),
    ],
    [dailyCycleKey, randomMissionCycleKey, selectedRandomMissions, shownDailyMissions, shownWeeklyMissions, weeklyCycleKey],
  );

  const completedMissionCount = missionCards.filter((mission) => missionDone[mission.id]).length;
  const successRate = Math.round((completedMissionCount / missionCards.length) * 100);

  const loadMissionRanking = async () => {
    setMissionRankingLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/missions/ranking?limit=10`);
      const body = await response.json();
      if (!response.ok) {
        setMissionRanking([]);
        return;
      }

      setMissionRanking(Array.isArray(body?.items) ? body.items.slice(0, 10) : []);
    } catch {
      setMissionRanking([]);
    } finally {
      setMissionRankingLoading(false);
    }
  };

  const loadMyMissionRank = async () => {
    if (!currentUserId) {
      setMyMissionRank(null);
      return;
    }

    setMyMissionRankLoading(true);
    try {
      const response = await fetch(`${apiBaseUrl}/missions/ranking/me?user_id=${encodeURIComponent(currentUserId)}`);
      const body = await response.json();
      if (!response.ok) {
        setMyMissionRank(null);
        return;
      }

      setMyMissionRank(body);
    } catch {
      setMyMissionRank(null);
    } finally {
      setMyMissionRankLoading(false);
    }
  };

  const loadBankLink = async (userId: string) => {
    try {
      const response = await fetch(`${apiBaseUrl}/bankapi/accounts/me?user_id=${encodeURIComponent(userId)}`);
      if (!response.ok) {
        setBankLink(null);
        return;
      }
      const body = (await response.json()) as BankApiLinkSummary;
      setBankLink(body);
    } catch {
      setBankLink(null);
    }
  };

  const loadBankHistory = async (userId: string) => {
    try {
      const [balanceResponse, txResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/bankapi/balance-history?user_id=${encodeURIComponent(userId)}&limit=20`),
        fetch(`${apiBaseUrl}/bankapi/transactions?user_id=${encodeURIComponent(userId)}&limit=20`),
      ]);

      if (balanceResponse.ok) {
        const balanceBody = await balanceResponse.json();
        setBankBalanceHistory(Array.isArray(balanceBody?.items) ? balanceBody.items : []);
      }

      if (txResponse.ok) {
        const txBody = await txResponse.json();
        const items = Array.isArray(txBody?.items) ? txBody.items : [];
        setBankTransactionHistory(items);
      }
    } catch {
      // ignore transient history load failures
    }
  };

  const pollBankApi = async (userId: string) => {
    setBankPolling(true);
    try {
      const response = await fetch(`${apiBaseUrl}/bankapi/poll?user_id=${encodeURIComponent(userId)}`, {
        method: "POST",
      });
      const body = await response.json();
      if (!response.ok) {
        setBankStatusMessage(body?.error?.message || "실계좌 조회에 실패했습니다.");
        return;
      }

      const pollResult = body as BankApiPollResult;
      setBankCurrentBalance(pollResult.current_balance);
      setHp(pollResult.hp);
      setBankStatusMessage(
        pollResult.new_transaction_count > 0
          ? `신규 거래 ${pollResult.new_transaction_count}건 반영, HP ${pollResult.total_hp_drop} 감소`
          : "신규 거래 없음",
      );
      await loadBankLink(userId);
      await loadBankHistory(userId);
    } catch {
      setBankStatusMessage("실계좌 조회 중 오류가 발생했습니다.");
    } finally {
      setBankPolling(false);
    }
  };

  const registerBankAccount = async () => {
    if (!currentUserId) {
      setBankStatusMessage("로그인 후 계좌를 등록해 주세요.");
      return;
    }

    if (!bankAccountNumber.trim() || !bankAccountPassword.trim() || !bankResidentNumber.trim()) {
      setBankStatusMessage("은행/계좌번호/계좌비밀번호/주민번호 앞 6자리를 입력해 주세요.");
      return;
    }

    setBankStatusMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/bankapi/accounts/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          bank_code: bankCode,
          account_number: bankAccountNumber.trim(),
          account_password: bankAccountPassword.trim(),
          resident_number: bankResidentNumber.trim(),
        }),
      });
      const raw = await response.text();
      let body: unknown = null;
      try {
        body = raw ? JSON.parse(raw) : null;
      } catch {
        body = null;
      }

      const parsedBody = body as {
        message?: string;
        detail?: { message?: string };
        error?: { message?: string; details?: unknown };
        link?: BankApiLinkSummary;
      } | null;

      if (!response.ok) {
        let errorMessage = "계좌 등록에 실패했습니다.";
        const detailMessage =
          parsedBody?.error?.message ||
          parsedBody?.detail?.message ||
          parsedBody?.message ||
          "";

        if (detailMessage) {
          errorMessage = `계좌 등록 실패 (${response.status}): ${detailMessage}`;
          const errorDetails = parsedBody?.error?.details;
          if (typeof errorDetails === "string" && errorDetails.trim()) {
            errorMessage += ` / ${errorDetails.trim()}`;
          }
        } else if (raw.trim()) {
          errorMessage = `계좌 등록 실패 (${response.status}): ${raw.trim()}`;
        }

        setBankStatusMessage(errorMessage);
        return;
      }

      setBankLink(parsedBody?.link || null);
      setBankStatusMessage(parsedBody?.message || "계좌 등록이 완료되었습니다.");
      await pollBankApi(currentUserId);
    } catch {
      setBankStatusMessage("계좌 등록 중 오류가 발생했습니다.");
    }
  };

  useEffect(() => {
    if (activeTab !== "랭킹" || !isLoggedIn) {
      setMyMissionRank(null);
      return;
    }

    loadMissionRanking();
    loadMyMissionRank();
  }, [activeTab, currentUserId, isLoggedIn]);

  useEffect(() => {
    if (!isLoggedIn || !currentUserId) {
      setBankLink(null);
      setBankBalanceHistory([]);
      setBankTransactionHistory([]);
      setBankCurrentBalance(null);
      return;
    }

    loadBankLink(currentUserId);
    loadBankHistory(currentUserId);
  }, [currentUserId, isLoggedIn]);

  useEffect(() => {
    if (!isLoggedIn || !currentUserId || !bankLink) {
      return;
    }

    pollBankApi(currentUserId);
    const timer = setInterval(() => {
      pollBankApi(currentUserId);
    }, 60000);

    return () => clearInterval(timer);
  }, [bankLink?.account_number_masked, bankLink?.bank_code, currentUserId, isLoggedIn]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const authorizationCode = params.get("code") || params.get("authorization_code");
    if (!authorizationCode) {
      return;
    }

    const stateParam = params.get("state");
    const storedUserId = window.localStorage.getItem("asset-helper-last-user-id") || "";
    const resolvedUserId =
      resolveOpenBankingUserId(stateParam, currentUserId) ||
      storedUserId.trim();

    if (!resolvedUserId) {
      setIsBankPanelOpen(true);
      setBankStatusMessage("오픈뱅킹 콜백은 받았지만 사용자 정보가 없어 연결할 수 없습니다. 다시 로그인 후 시도해 주세요.");
      return;
    }

    const processKey = `openbanking-callback-${resolvedUserId}-${authorizationCode}`;
    if (window.sessionStorage.getItem(processKey)) {
      return;
    }
    window.sessionStorage.setItem(processKey, "1");

    setIsBankPanelOpen(true);
    setBankStatusMessage("오픈뱅킹 콜백을 처리 중입니다...");

    const run = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/openbanking/connect`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: resolvedUserId,
            authorization_code: authorizationCode,
          }),
        });

        const body = await response.json();
        if (!response.ok) {
          const message = body?.error?.message || body?.message || "오픈뱅킹 연결에 실패했습니다.";
          setBankStatusMessage(`오픈뱅킹 연결 실패: ${message}`);
          return;
        }

        setCurrentUserId((prev) => prev || resolvedUserId);
        setBankStatusMessage("오픈뱅킹 연결이 완료되었습니다.");
      } catch {
        setBankStatusMessage("오픈뱅킹 콜백 처리 중 오류가 발생했습니다.");
      } finally {
        const nextParams = new URLSearchParams(window.location.search);
        nextParams.delete("code");
        nextParams.delete("authorization_code");
        nextParams.delete("state");
        const nextSearch = nextParams.toString();
        const nextUrl = `${window.location.pathname}${nextSearch ? `?${nextSearch}` : ""}${window.location.hash}`;
        window.history.replaceState({}, "", nextUrl);
      }
    };

    void run();
  }, [apiBaseUrl, currentUserId]);

  const completeMissionFromUi = async (missionId: string) => {
    if (missionDone[missionId]) {
      return;
    }

    setMissionDone((prev) => ({
      ...prev,
      [missionId]: true,
    }));

    if (!currentUserId) {
      setMissionCompleteMessage("로그인 후 완료하면 계정 랭킹에 반영됩니다.");
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/missions/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: currentUserId }),
      });
      const body = await response.json();
      if (!response.ok) {
        setMissionCompleteMessage(body?.error?.message || "미션 완료 저장에 실패했습니다.");
        return;
      }

      setMissionCompleteMessage(`계정 누적 미션 완료 수: ${body.completed_count}`);
      await loadMissionRanking();
      await loadMyMissionRank();
    } catch {
      setMissionCompleteMessage("미션 완료 저장 중 오류가 발생했습니다.");
    }
  };

  const portfolioValue = useMemo(() => {
    const stockValue = companies.reduce((sum, company) => {
      const qty = holdings[company.symbol] || 0;
      return sum + company.price * qty;
    }, 0);
    return cash + stockValue;
  }, [cash, companies, holdings]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCompanies((prev) =>
        prev.map((company) => {
          const randomShock = (Math.random() - 0.5) * company.volatility;
          const orderMomentum = company.orderPressure * 0.12;
          const movePct = (company.drift + randomShock + orderMomentum) / 100;

          const nextPrice = Math.max(100, Math.round(company.price * (1 + movePct)));
          const decayedPressure = company.orderPressure * 0.86;
          const nextPressure = Math.abs(decayedPressure) < 0.0001 ? 0 : decayedPressure;

          return {
            ...company,
            price: nextPrice,
            lastChange: nextPrice - company.price,
            orderPressure: nextPressure,
          };
        }),
      );
    }, 1200);

    return () => clearInterval(timer);
  }, []);

  const handleTrade = (symbol: string, side: "buy" | "sell") => {
    const company = companies.find((item) => item.symbol === symbol);
    if (!company) {
      return;
    }

    const rawQty = tradeQuantity[symbol] || "1";
    const qty = Number.parseInt(rawQty, 10);
    if (!Number.isFinite(qty) || qty <= 0) {
      setTradeMessage("수량은 1주 이상 입력해 주세요.");
      return;
    }

    const impactRatio = qty / company.liquidity;
    const executionPrice = Math.max(
      100,
      Math.round(company.price * (1 + (side === "buy" ? 1 : -1) * impactRatio * 0.35)),
    );
    const fee = Math.round(executionPrice * qty * 0.0015);

    if (side === "buy") {
      const totalCost = executionPrice * qty + fee;
      if (totalCost > cash) {
        setTradeMessage("예수금이 부족합니다.");
        return;
      }

      setCash((prev) => prev - totalCost);
      setHoldings((prev) => ({ ...prev, [symbol]: (prev[symbol] || 0) + qty }));
      setCompanies((prev) =>
        prev.map((item) =>
          item.symbol === symbol
            ? {
                ...item,
                price: executionPrice,
                lastChange: executionPrice - item.price,
                orderPressure: item.orderPressure + impactRatio,
              }
            : item,
        ),
      );
      setTradeMessage(`${company.name} ${qty}주 매수 체결 (${formatKrw(executionPrice)} / 수수료 ${formatKrw(fee)})`);
      return;
    }

    const owned = holdings[symbol] || 0;
    if (owned < qty) {
      setTradeMessage(`보유 수량이 부족합니다. 현재 ${owned}주 보유 중입니다.`);
      return;
    }

    const proceeds = executionPrice * qty - fee;
    setCash((prev) => prev + proceeds);
    setHoldings((prev) => ({ ...prev, [symbol]: owned - qty }));
    setCompanies((prev) =>
      prev.map((item) =>
        item.symbol === symbol
          ? {
              ...item,
              price: executionPrice,
              lastChange: executionPrice - item.price,
              orderPressure: item.orderPressure - impactRatio,
            }
          : item,
      ),
    );
    setTradeMessage(`${company.name} ${qty}주 매도 체결 (${formatKrw(executionPrice)} / 수수료 ${formatKrw(fee)})`);
  };

  const onSignup = async () => {
    setSignupMessage("");
    const normalizedUserId = signupUserId.trim();
    const normalizedPassword = signupPassword.trim();
    const normalizedNickname = signupNickname.trim();

    if (!normalizedUserId || !normalizedPassword || !normalizedNickname) {
      setSignupMessage("아이디, 비밀번호, 닉네임을 입력해 주세요.");
      return;
    }

    const normalizedBaseline = Number(baseline.replaceAll(",", "").trim());
    const signupPayload: Record<string, unknown> = {
      user_id: normalizedUserId,
      password: normalizedPassword,
      nickname: normalizedNickname,
      email: email.trim(),
    };

    if (Number.isFinite(normalizedBaseline) && normalizedBaseline > 0) {
      signupPayload.baseline_amount = normalizedBaseline;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(signupPayload),
      });

      const body = await response.json();
      if (!response.ok) {
        const message = body?.error?.message;
        setSignupMessage(message || "회원가입에 실패했습니다.");
        return;
      }

      setSignupMessage("회원가입이 완료되었습니다.");
      setLoginUserId(normalizedUserId);
      setLoginPassword(normalizedPassword);
      setLoginMessage("");
      setAuthView("login");
    } catch {
      setSignupMessage("회원가입 중 오류가 발생했습니다.");
    }
  };

  const onLogin = async () => {
    setLoginMessage("");
    const normalizedUserId = loginUserId.trim();
    const normalizedPassword = loginPassword.trim();

    if (!normalizedUserId || !normalizedPassword) {
      setLoginMessage("아이디와 비밀번호를 입력해 주세요.");
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: normalizedUserId,
          password: normalizedPassword,
        }),
      });

      const body = await response.json();
      if (!response.ok) {
        setLoginMessage(body?.error?.message || "로그인에 실패했습니다.");
        return;
      }

      const nickname = body?.nickname || signupNickname || loginUserId;
      setIsLoggedIn(true);
      setCurrentUserId(body.user_id || normalizedUserId);
      window.localStorage.setItem("asset-helper-last-user-id", body.user_id || normalizedUserId);
      setLoggedInNickname(nickname);
      setIsAuthPanelOpen(false);
      setLoginMessage(`로그인 성공: ${body.user_id}`);
    } catch {
      setLoginMessage("로그인 중 오류가 발생했습니다.");
    }
  };

  const onLogout = () => {
    setIsLoggedIn(false);
    setCurrentUserId("");
    setLoggedInNickname("");
    setIsAuthPanelOpen(false);
    setIsBankPanelOpen(false);
    setBankLink(null);
    setBankBalanceHistory([]);
    setBankTransactionHistory([]);
    setBankCurrentBalance(null);
    setBankStatusMessage("");
    setBankPolling(false);
    window.localStorage.removeItem("asset-helper-last-user-id");
    setLoginMessage("");
    setSignupMessage("");
  };

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: responsiveStyles }} />
      <main
      style={{
        maxWidth: "100%",
        margin: "0 auto",
        padding: "clamp(20px, 5vw, 64px) clamp(12px, 3vw, 24px) 140px",
      }}
    >
      {activeTab === "홈" ? (
      <section
        style={{
          background: "linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(240,248,255,0.86) 100%)",
          border: "1px solid var(--border)",
          borderRadius: "clamp(20px, 4vw, 28px)",
          boxShadow: "var(--shadow)",
          padding: "clamp(20px, 4vw, 32px)",
          backdropFilter: "blur(12px)",
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: "clamp(24px, 8vw, 44px)",
            lineHeight: 1.1,
            letterSpacing: "-0.05em",
            background: "linear-gradient(135deg, #0f172a 0%, #2563eb 45%, #06b6d4 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          자산 도우미
        </h1>

        {isLoggedIn ? (
          <div style={{ margin: "18px 0 0", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10, width: "100%" }}>
            <div
              aria-label="logged-in-nickname"
              style={{
                display: "inline-flex",
                alignItems: "center",
                borderRadius: 999,
                background: "linear-gradient(135deg, rgba(37,99,235,0.12), rgba(6,182,212,0.12))",
                color: "#0f172a",
                padding: "10px 16px",
                fontSize: 14,
                fontWeight: 700,
                flex: "0 1 auto",
              }}
            >
              {loggedInNickname} 님
            </div>
            <button
              type="button"
              aria-label="logout-button"
              onClick={onLogout}
              style={{
                border: "none",
                borderRadius: 999,
                background: "linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)",
                color: "white",
                padding: "10px 14px",
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
                marginLeft: "auto",
              }}
            >
              로그아웃
            </button>
          </div>
        ) : (
          <button
            type="button"
            aria-label="auth-panel-toggle"
            onClick={() => setIsAuthPanelOpen((prev) => !prev)}
            style={{
              marginTop: 18,
              border: "none",
              borderRadius: 999,
              background: "linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)",
              color: "white",
              padding: "10px 16px",
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            로그인/회원가입
          </button>
        )}

        {isLoggedIn ? (
          <div
            style={{
              marginTop: 28,
              padding: 20,
              borderRadius: 20,
              background: "#f8fafc",
              border: "1px solid #e2e8f0",
            }}
          >
            <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "#0f172a" }}>온보딩</p>
            <div
              style={{
                display: "grid",
                gap: 16,
                marginTop: 16,
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              }}
            >
              <label style={{ display: "grid", gap: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 600 }}>분신 타입</span>
                <select
                  aria-label="avatar-type-select"
                  value={avatarType}
                  onChange={(event) => setAvatarType(event.target.value)}
                  style={{
                    borderRadius: 14,
                    border: "1px solid #cbd5e1",
                    padding: "14px 16px",
                    fontSize: 16,
                    background: "white",
                  }}
                >
                  <option value="plant">식물</option>
                  <option value="character">캐릭터</option>
                </select>
              </label>

              <label style={{ display: "grid", gap: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 600 }}>시들기 강도</span>
                <select
                  aria-label="intensity-select"
                  value={intensity}
                  onChange={(event) => setIntensity(event.target.value)}
                  style={{
                    borderRadius: 14,
                    border: "1px solid #cbd5e1",
                    padding: "14px 16px",
                    fontSize: 16,
                    background: "white",
                  }}
                >
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                </select>
              </label>
            </div>

            <div style={{ marginTop: 18, fontSize: 14, color: "#475569" }} data-testid="onboarding-summary">
              {`${avatarType} · 강도 ${intensity}`}
            </div>

          </div>
        ) : null}

        {isLoggedIn ? (
          <div
            style={{
              marginTop: 24,
              padding: 20,
              borderRadius: 20,
              background: "linear-gradient(180deg, rgba(255,255,255,0.84) 0%, rgba(240,248,255,0.72) 100%)",
              border: "1px solid var(--border)",
              display: "grid",
              gap: 14,
              boxShadow: "0 18px 50px rgba(15, 23, 42, 0.06)",
            }}
          >
            <button
              type="button"
              onClick={() => setIsBankPanelOpen((prev) => !prev)}
              aria-label="bank-panel-toggle"
              aria-expanded={isBankPanelOpen}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
                border: "none",
                background: "transparent",
                padding: 0,
                cursor: "pointer",
                textAlign: "left",
              }}
            >
              <p style={{ margin: 0, fontSize: 15, fontWeight: 800, color: "var(--text)" }}>실계좌 연동 및 실시간 조회(1분)</p>
              <span style={{ fontSize: 18, fontWeight: 900, color: "var(--primary)", lineHeight: 1 }}>
                {isBankPanelOpen ? "▴" : "▾"}
              </span>
            </button>

            {isBankPanelOpen ? (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
                  <label style={{ display: "grid", gap: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>은행</span>
                    <select
                      onChange={(event) => setBankCode(event.target.value)}
                      style={{ borderRadius: 10, border: "1px solid #cbd5e1", padding: "10px 12px", background: "white" }}
                    >
                      <option value="NH">NH</option>
                      <option value="KB">KB</option>
                      <option value="WR">WR</option>
                    </select>
                  </label>

                  <label style={{ display: "grid", gap: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>계좌번호</span>
                    <input
                      value={bankAccountNumber}
                      onChange={(event) => setBankAccountNumber(event.target.value)}
                      style={{ borderRadius: 10, border: "1px solid #cbd5e1", padding: "10px 12px" }}
                    />
                  </label>

                  <label style={{ display: "grid", gap: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>계좌 비밀번호</span>
                    <input
                      type="password"
                      value={bankAccountPassword}
                      onChange={(event) => setBankAccountPassword(event.target.value)}
                      style={{ borderRadius: 10, border: "1px solid #cbd5e1", padding: "10px 12px" }}
                    />
                  </label>

                  <label style={{ display: "grid", gap: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>주민번호 앞 6자리</span>
                    <input
                      value={bankResidentNumber}
                      onChange={(event) => setBankResidentNumber(event.target.value)}
                      maxLength={6}
                      style={{ borderRadius: 10, border: "1px solid #cbd5e1", padding: "10px 12px" }}
                    />
                  </label>
                </div>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <button
                    type="button"
                    onClick={registerBankAccount}
                    style={{ border: "none", borderRadius: 999, background: "#0f172a", color: "white", padding: "10px 16px", fontWeight: 700, cursor: "pointer" }}
                  >
                    계좌 등록
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (currentUserId) {
                        pollBankApi(currentUserId);
                      }
                    }}
                    style={{ border: "1px solid #0f172a", borderRadius: 999, background: "white", color: "#0f172a", padding: "10px 16px", fontWeight: 700, cursor: "pointer" }}
                  >
                    지금 조회
                  </button>
                  {bankPolling ? <span style={{ fontSize: 13, color: "#475569", alignSelf: "center" }}>조회 중...</span> : null}
                </div>

                {bankLink ? (
                  <div style={{ fontSize: 13, color: "#334155", lineHeight: 1.5 }}>
                    연동 계좌: {bankLink.bank_code} {bankLink.account_number_masked} · 마지막 조회: {bankLink.last_polled_at || "없음"}
                  </div>
                ) : (
                  <div style={{ fontSize: 13, color: "#64748b" }}>아직 연동된 계좌가 없습니다.</div>
                )}

                {bankCurrentBalance !== null ? (
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>현재 잔액: {formatKrw(bankCurrentBalance)}</div>
                ) : null}

                {bankStatusMessage ? <div style={{ fontSize: 13, color: "#334155" }}>{bankStatusMessage}</div> : null}

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10 }}>
                  <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: 12, background: "#f8fafc" }}>
                    <strong style={{ fontSize: 13 }}>최근 잔액 기록</strong>
                    <div style={{ marginTop: 8, display: "grid", gap: 6 }}>
                      {[...bankBalanceHistory].reverse().slice(0, 5).map((point) => (
                        <div key={`${point.polled_at}-${point.balance}`} style={{ fontSize: 12, color: "#334155" }}>
                          {point.polled_at} · {formatKrw(point.balance)}
                        </div>
                      ))}
                      {bankBalanceHistory.length === 0 ? <div style={{ fontSize: 12, color: "#64748b" }}>기록 없음</div> : null}
                    </div>
                  </div>

                  <div style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: 12, background: "#f8fafc" }}>
                    <strong style={{ fontSize: 13 }}>최근 거래내역</strong>
                    <div style={{ marginTop: 8, display: "grid", gap: 6 }}>
                      {[...bankTransactionHistory].reverse().slice(0, 5).map((tx, index) => (
                        <div key={`${tx.date}-${tx.time}-${tx.amount}-${index}`} style={{ fontSize: 12, color: "#334155" }}>
                          {tx.date} {tx.time} · {tx.type === "withdrawal" ? "출금" : "입금"} {formatKrw(tx.amount)} · 잔액 {formatKrw(tx.balance)}
                        </div>
                      ))}
                      {bankTransactionHistory.length === 0 ? <div style={{ fontSize: 12, color: "#64748b" }}>거래내역 없음</div> : null}
                    </div>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        ) : null}

        {isAuthPanelOpen ? (
          <div
            role="presentation"
            onClick={() => setIsAuthPanelOpen(false)}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 1200,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "16px",
              background: "linear-gradient(180deg, rgba(15,23,42,0.58) 0%, rgba(15,23,42,0.48) 100%)",
              backdropFilter: "blur(12px)",
            }}
          >
            <div
              role="dialog"
              aria-modal="true"
              aria-label="auth-modal"
              onClick={(event) => event.stopPropagation()}
              style={{
                width: "min(92vw, 760px)",
                maxHeight: "calc(100vh - 32px)",
                overflowY: "auto",
                borderRadius: 24,
                background: "linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(238,247,255,0.96) 100%)",
                border: "1px solid rgba(148,163,184,0.20)",
                boxShadow: "0 32px 100px rgba(15,23,42,0.28)",
                padding: 20,
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
                <div>
                  <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "#9a3412" }}>인증</p>
                  <h2 style={{ margin: "6px 0 0", fontSize: 24, color: "#431407" }}>
                    {authView === "signup" ? "회원가입" : "로그인"}
                  </h2>
                </div>
                <button
                  type="button"
                  aria-label="auth-panel-close"
                  onClick={() => setIsAuthPanelOpen(false)}
                  style={{
                    border: "1px solid #fdba74",
                    borderRadius: 999,
                    background: "white",
                    color: "#1d4ed8",
                    padding: "8px 14px",
                    fontSize: 14,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  닫기
                </button>
              </div>

              <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
                <button
                  type="button"
                  onClick={() => {
                    setAuthView("signup");
                    setLoginMessage("");
                  }}
                  style={{
                      border: authView === "signup" ? "none" : "1px solid rgba(37,99,235,0.22)",
                    borderRadius: 999,
                      background: authView === "signup" ? "var(--primary)" : "white",
                    color: authView === "signup" ? "white" : "#9a3412",
                    padding: "8px 14px",
                    fontSize: 14,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  회원가입
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAuthView("login");
                    setSignupMessage("");
                  }}
                  style={{
                      border: authView === "login" ? "none" : "1px solid rgba(37,99,235,0.22)",
                    borderRadius: 999,
                      background: authView === "login" ? "var(--primary)" : "white",
                      color: authView === "login" ? "white" : "#1d4ed8",
                    padding: "8px 14px",
                    fontSize: 14,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  로그인
                </button>
              </div>

              {authView === "signup" ? (
                <>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                      gap: 16,
                      marginTop: 16,
                    }}
                  >
                    <label style={{ display: "grid", gap: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>회원가입 아이디</span>
                      <input
                        aria-label="signup-user-id"
                        value={signupUserId}
                        onChange={(event) => setSignupUserId(event.target.value)}
                        style={{ borderRadius: 14, border: "1px solid rgba(148,163,184,0.30)", padding: "14px 16px", fontSize: 16 }}
                      />
                    </label>
                    <label style={{ display: "grid", gap: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>회원가입 비밀번호</span>
                      <input
                        aria-label="signup-password"
                        type="password"
                        value={signupPassword}
                        onChange={(event) => setSignupPassword(event.target.value)}
                        style={{ borderRadius: 14, border: "1px solid rgba(148,163,184,0.30)", padding: "14px 16px", fontSize: 16 }}
                      />
                    </label>
                    <label style={{ display: "grid", gap: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>회원가입 닉네임</span>
                      <input
                        aria-label="signup-nickname"
                        value={signupNickname}
                        onChange={(event) => setSignupNickname(event.target.value)}
                        style={{ borderRadius: 14, border: "1px solid rgba(148,163,184,0.30)", padding: "14px 16px", fontSize: 16 }}
                      />
                    </label>
                  </div>

                  <button
                    type="button"
                    aria-label="signup-submit"
                    onClick={onSignup}
                    style={{ marginTop: 16, border: "none", borderRadius: 999, background: "linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)", color: "white", padding: "12px 18px", fontSize: 15, fontWeight: 700, cursor: "pointer", boxShadow: "0 12px 26px rgba(37,99,235,0.22)" }}
                  >
                    회원가입
                  </button>

                  {signupMessage ? (
                    <p data-testid="signup-message" style={{ margin: "10px 0 0", color: "#7c2d12", fontSize: 14 }}>
                      {signupMessage}
                    </p>
                  ) : null}
                </>
              ) : (
                <>
                  <div style={{ marginTop: 16, display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
                    <label style={{ display: "grid", gap: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>로그인 아이디</span>
                      <input
                        aria-label="login-user-id"
                        value={loginUserId}
                        onChange={(event) => setLoginUserId(event.target.value)}
                        style={{ borderRadius: 14, border: "1px solid rgba(148,163,184,0.30)", padding: "14px 16px", fontSize: 16 }}
                      />
                    </label>
                    <label style={{ display: "grid", gap: 8 }}>
                      <span style={{ fontSize: 14, fontWeight: 600 }}>로그인 비밀번호</span>
                      <input
                        aria-label="login-password"
                        type="password"
                        value={loginPassword}
                        onChange={(event) => setLoginPassword(event.target.value)}
                        style={{ borderRadius: 14, border: "1px solid rgba(148,163,184,0.30)", padding: "14px 16px", fontSize: 16 }}
                      />
                    </label>
                  </div>

                  <button
                    type="button"
                    aria-label="login-submit"
                    onClick={onLogin}
                    style={{ marginTop: 14, border: "1px solid rgba(37,99,235,0.22)", borderRadius: 999, background: "white", color: "var(--primary-strong)", padding: "12px 18px", fontSize: 15, fontWeight: 700, cursor: "pointer" }}
                  >
                    로그인
                  </button>

                  {loginMessage ? (
                    <p data-testid="login-message" style={{ margin: "10px 0 0", color: "#7c2d12", fontSize: 14 }}>
                      {loginMessage}
                    </p>
                  ) : null}
                </>
              )}
            </div>
          </div>
        ) : null}

        <article
          style={{
            marginTop: 28,
            padding: 24,
            borderRadius: 20,
            background: "linear-gradient(135deg, #0f172a 0%, #334155 100%)",
            color: "white",
          }}
        >
          <div
            style={{
              display: "grid",
              gap: 16,
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              alignItems: "center",
            }}
          >
            <div>
              <p style={{ margin: 0, fontSize: 14, opacity: 0.78 }}>현재 분신 상태</p>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 10 }}>
                <strong data-testid="hp-value" style={{ fontSize: 64, lineHeight: 1 }}>
                  {hp}
                </strong>
                <span style={{ fontSize: 20 }}>HP</span>
              </div>
              <p style={{ margin: "12px 0 0", fontSize: 16, opacity: 0.88 }}>
                {hp === 0 ? "회복 액션을 권장합니다." : "안정 범위입니다."}
              </p>
            </div>
            <img
              src={avatarType === "character" ? "/캐릭터.png" : "/해바라기.png"}
              alt={avatarType === "character" ? "캐릭터 분신" : "식물 분신"}
              style={{
                width: "100%",
                maxWidth: 260,
                justifySelf: "center",
                borderRadius: 12,
                border: "1px solid rgba(226,232,240,0.35)",
                objectFit: "cover",
                background: "rgba(255,255,255,0.08)",
              }}
            />
          </div>
        </article>
      </section>
      ) : null}

      {activeTab === "주식" ? (
        <section
          style={{
            background: "rgba(255,255,255,0.92)",
            border: "1px solid rgba(148,163,184,0.24)",
            borderRadius: 24,
            boxShadow: "0 24px 80px rgba(15,23,42,0.08)",
            padding: 24,
          }}
        >
          {!isLoggedIn ? (
            <p style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#b91c1c" }}>로그인하십시오.</p>
          ) : (
            <>
              <h2 style={{ margin: 0, fontSize: 28 }}>모의 주식 시장</h2>
              <p style={{ margin: "10px 0 0", color: "#475569", lineHeight: 1.5 }}>
                가격은 기본 추세, 무작위 변동성, 그리고 주문으로 발생한 수요/공급 압력이 합쳐져 실시간으로 변합니다.
              </p>

              <div
                style={{
                  marginTop: 16,
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 12,
                }}
              >
                <div style={{ border: "1px solid #e2e8f0", borderRadius: 14, padding: 14, background: "#f8fafc" }}>
                  <div style={{ fontSize: 13, color: "#64748b" }}>예수금</div>
                  <div style={{ marginTop: 6, fontSize: 20, fontWeight: 800 }}>{formatKrw(cash)}</div>
                </div>
                <div style={{ border: "1px solid #e2e8f0", borderRadius: 14, padding: 14, background: "#f8fafc" }}>
                  <div style={{ fontSize: 13, color: "#64748b" }}>총 자산</div>
                  <div style={{ marginTop: 6, fontSize: 20, fontWeight: 800 }}>{formatKrw(portfolioValue)}</div>
                </div>
              </div>

              {tradeMessage ? (
                <p style={{ margin: "14px 0 0", fontSize: 14, color: "#334155" }}>{tradeMessage}</p>
              ) : null}

              <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
                {companies.map((company) => {
                  const changeColor = company.lastChange >= 0 ? "#b91c1c" : "#1d4ed8";
                  const owned = holdings[company.symbol] || 0;
                  const parsedQty = Number.parseInt(tradeQuantity[company.symbol] || "1", 10);
                  const qty = Number.isFinite(parsedQty) && parsedQty > 0 ? parsedQty : 0;
                  const estimatedBuyPrice = qty > 0 ? estimateExecutionPrice(company, qty, "buy") : 0;
                  const estimatedBuyFee = qty > 0 ? Math.round(estimatedBuyPrice * qty * 0.0015) : 0;
                  const estimatedBuyTotal = qty > 0 ? estimatedBuyPrice * qty + estimatedBuyFee : 0;

                  return (
                    <article
                      key={company.symbol}
                      style={{
                        border: "1px solid #e2e8f0",
                        borderRadius: 16,
                        padding: 14,
                        display: "grid",
                        gap: 10,
                        background: "white",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
                        <div>
                          <strong style={{ fontSize: 17 }}>{company.name}</strong>
                          <div style={{ fontSize: 12, color: "#64748b" }}>{company.symbol}</div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ fontSize: 19, fontWeight: 800 }}>{formatKrw(company.price)}</div>
                          <div style={{ fontSize: 13, color: changeColor }}>
                            {company.lastChange >= 0 ? "+" : ""}
                            {formatKrw(company.lastChange)}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                        <label style={{ fontSize: 13, color: "#334155" }}>수량</label>
                        <input
                          value={tradeQuantity[company.symbol] || "1"}
                          onChange={(event) =>
                            setTradeQuantity((prev) => ({
                              ...prev,
                              [company.symbol]: event.target.value,
                            }))
                          }
                          inputMode="numeric"
                          style={{
                            width: 86,
                            borderRadius: 10,
                            border: "1px solid #cbd5e1",
                            padding: "8px 10px",
                            fontSize: 14,
                          }}
                        />
                        <button
                          type="button"
                          onClick={() => handleTrade(company.symbol, "buy")}
                          style={{
                            border: "none",
                            borderRadius: 10,
                            background: "#dc2626",
                            color: "white",
                            padding: "8px 12px",
                            fontWeight: 700,
                            cursor: "pointer",
                          }}
                        >
                          매수
                        </button>
                        <button
                          type="button"
                          onClick={() => handleTrade(company.symbol, "sell")}
                          style={{
                            border: "none",
                            borderRadius: 10,
                            background: "#1d4ed8",
                            color: "white",
                            padding: "8px 12px",
                            fontWeight: 700,
                            cursor: "pointer",
                          }}
                        >
                          매도
                        </button>
                        <span style={{ marginLeft: "auto", fontSize: 13, color: "#475569" }}>보유 {owned}주</span>
                      </div>

                      <div style={{ fontSize: 13, color: "#334155", background: "#f8fafc", borderRadius: 10, padding: "8px 10px" }}>
                        {qty > 0
                          ? `예상 매수 필요금액: ${formatKrw(estimatedBuyTotal)} (예상 체결가 ${formatKrw(estimatedBuyPrice)} + 수수료 ${formatKrw(estimatedBuyFee)})`
                          : "수량을 입력하면 예상 매수 필요금액이 표시됩니다."}
                      </div>
                    </article>
                  );
                })}
              </div>
            </>
          )}
        </section>
      ) : null}

      {activeTab === "미션" ? (
        <section
          style={{
            background: "rgba(255,255,255,0.92)",
            border: "1px solid rgba(148,163,184,0.24)",
            borderRadius: 24,
            boxShadow: "0 24px 80px rgba(15,23,42,0.08)",
            padding: 24,
          }}
        >
          {!isLoggedIn ? (
            <p style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#b91c1c" }}>로그인하십시오.</p>
          ) : (
            <>
              <h2 style={{ margin: 0, fontSize: 28 }}>미션</h2>

          <div style={{ marginTop: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <strong style={{ fontSize: 15 }}>성공률</strong>
              <span style={{ fontSize: 14, color: "#334155" }}>
                {completedMissionCount}/{missionCards.length} ({successRate}%)
              </span>
            </div>
            <div
              style={{
                width: "100%",
                height: 12,
                borderRadius: 999,
                background: "#e2e8f0",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${successRate}%`,
                  height: "100%",
                  background: "linear-gradient(90deg, #16a34a 0%, #22c55e 100%)",
                  transition: "width 0.25s ease",
                }}
              />
            </div>
          </div>

          <div style={{ marginTop: 18 }}>
            <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>일일 미션 (5개)</h3>
            <div style={{ display: "grid", gap: 8 }}>
              {shownDailyMissions.map((mission, index) => {
                const id = `${dailyCycleKey}-daily-${index}`;
                return (
                  <div
                    key={id}
                    style={{
                      display: "flex",
                      gap: 10,
                      alignItems: "center",
                      justifyContent: "space-between",
                      border: "1px solid #e2e8f0",
                      borderRadius: 12,
                      padding: "10px 12px",
                      background: missionDone[id] ? "#f0fdf4" : "white",
                    }}
                  >
                    <span style={{ fontSize: 14, color: "#0f172a", paddingRight: 10 }}>{mission}</span>
                    {missionDone[id] ? (
                      <span style={{ fontSize: 13, fontWeight: 700, color: "#15803d", whiteSpace: "nowrap" }}>미션 완료</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => completeMissionFromUi(id)}
                        style={{
                          border: "none",
                          borderRadius: 8,
                          background: "#16a34a",
                          color: "white",
                          padding: "7px 10px",
                          fontSize: 13,
                          fontWeight: 700,
                          cursor: "pointer",
                          whiteSpace: "nowrap",
                        }}
                      >
                        완료
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ marginTop: 18 }}>
            <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>주간 미션 (5개)</h3>
            <div style={{ display: "grid", gap: 8 }}>
              {shownWeeklyMissions.map((mission, index) => {
                const id = `${weeklyCycleKey}-weekly-${index}`;
                return (
                  <div
                    key={id}
                    style={{
                      display: "flex",
                      gap: 10,
                      alignItems: "center",
                      justifyContent: "space-between",
                      border: "1px solid #e2e8f0",
                      borderRadius: 12,
                      padding: "10px 12px",
                      background: missionDone[id] ? "#eff6ff" : "white",
                    }}
                  >
                    <span style={{ fontSize: 14, color: "#0f172a", paddingRight: 10 }}>{mission}</span>
                    {missionDone[id] ? (
                      <span style={{ fontSize: 13, fontWeight: 700, color: "#1d4ed8", whiteSpace: "nowrap" }}>미션 완료</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => completeMissionFromUi(id)}
                        style={{
                          border: "none",
                          borderRadius: 8,
                          background: "#2563eb",
                          color: "white",
                          padding: "7px 10px",
                          fontSize: 13,
                          fontWeight: 700,
                          cursor: "pointer",
                          whiteSpace: "nowrap",
                        }}
                      >
                        완료
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ marginTop: 18 }}>
            <h3 style={{ margin: "0 0 10px", fontSize: 18 }}>랜덤 미션 (2개)</h3>
            <div style={{ display: "grid", gap: 8 }}>
              {selectedRandomMissions.map((mission, index) => {
                const id = `${randomMissionCycleKey}-random-${index}`;
                return (
                  <div
                    key={id}
                    style={{
                      display: "flex",
                      gap: 10,
                      alignItems: "center",
                      justifyContent: "space-between",
                      border: "1px solid #e2e8f0",
                      borderRadius: 12,
                      padding: "10px 12px",
                      background: missionDone[id] ? "#fff7ed" : "white",
                    }}
                  >
                    <span style={{ fontSize: 14, color: "#0f172a", paddingRight: 10 }}>{mission}</span>
                    {missionDone[id] ? (
                      <span style={{ fontSize: 13, fontWeight: 700, color: "#c2410c", whiteSpace: "nowrap" }}>미션 완료</span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => completeMissionFromUi(id)}
                        style={{
                          border: "none",
                          borderRadius: 8,
                          background: "#ea580c",
                          color: "white",
                          padding: "7px 10px",
                          fontSize: 13,
                          fontWeight: 700,
                          cursor: "pointer",
                          whiteSpace: "nowrap",
                        }}
                      >
                        완료
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

              {missionCompleteMessage ? (
                <p style={{ margin: "14px 0 0", fontSize: 14, color: "#334155" }}>{missionCompleteMessage}</p>
              ) : null}
            </>
          )}
        </section>
      ) : null}

      {activeTab === "랭킹" ? (
        <section
          style={{
            background: "rgba(255,255,255,0.92)",
            border: "1px solid rgba(148,163,184,0.24)",
            borderRadius: 24,
            boxShadow: "0 24px 80px rgba(15,23,42,0.08)",
            padding: 24,
          }}
        >
          {!isLoggedIn ? (
            <p style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#b91c1c" }}>로그인하십시오.</p>
          ) : (
            <>
              <h2 style={{ margin: 0, fontSize: 28 }}>랭킹</h2>
              <p style={{ margin: "10px 0 0", color: "#475569" }}>미션 완료 누적 수가 많은 계정 순으로 표시됩니다.</p>

              {missionRankingLoading ? <p style={{ marginTop: 12 }}>랭킹을 불러오는 중...</p> : null}

              {missionRankingLoading ? null : (
                <div style={{ marginTop: 14, display: "grid", gap: 8 }}>
                  {missionRanking.length === 0 ? (
                    <p style={{ margin: 0, color: "#64748b" }}>표시할 랭킹 데이터가 없습니다.</p>
                  ) : (
                    missionRanking.map((item) => (
                      <article
                        key={item.user_id}
                        style={{
                          border: "1px solid #e2e8f0",
                          borderRadius: 12,
                          padding: "10px 12px",
                          background: item.rank <= 3 ? "#f8fafc" : "white",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: 10,
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <strong style={{ width: 28, textAlign: "center" }}>{item.rank}</strong>
                          <div style={{ fontWeight: 700 }}>{item.nickname}</div>
                        </div>
                        <div style={{ fontWeight: 700, color: "#0f172a" }}>{item.completed_count}회</div>
                      </article>
                    ))
                  )}
                </div>
              )}

              <div
                style={{
                  marginTop: 14,
                  border: "1px solid #cbd5e1",
                  borderRadius: 12,
                  background: "#f8fafc",
                  padding: "10px 12px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <strong style={{ fontSize: 14, color: "#0f172a" }}>내 계정 순위</strong>
                {myMissionRankLoading ? (
                  <span style={{ fontSize: 13, color: "#475569" }}>불러오는 중...</span>
                ) : myMissionRank ? (
                  <span style={{ fontSize: 14, fontWeight: 800, color: "#0f172a" }}>
                    {myMissionRank.rank}위 ({myMissionRank.completed_count}회)
                  </span>
                ) : (
                  <span style={{ fontSize: 13, color: "#64748b" }}>순위 정보를 찾을 수 없습니다.</span>
                )}
              </div>
            </>
          )}
        </section>
      ) : null}

      <nav
        aria-label="bottom-nav"
        style={{
          position: "fixed",
          left: "50%",
          bottom: 16,
          transform: "translateX(-50%)",
          width: "min(720px, calc(100% - 24px))",
          background: "rgba(255,255,255,0.96)",
          border: "1px solid #e2e8f0",
          borderRadius: 20,
          boxShadow: "0 12px 30px rgba(15,23,42,0.12)",
          backdropFilter: "blur(10px)",
          padding: "10px 12px",
          zIndex: 20,
        }}
      >
        <ul
          style={{
            margin: 0,
            padding: 0,
            listStyle: "none",
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: 8,
          }}
        >
          {menuTabs.map((menu) => (
            <li key={menu}>
              <button
                type="button"
                aria-label={`bottom-menu-${menu}`}
                onClick={() => setActiveTab(menu)}
                style={{
                  width: "100%",
                  border: "none",
                  borderRadius: 14,
                  background: menu === activeTab ? "#0f172a" : "#f8fafc",
                  color: menu === activeTab ? "white" : "#0f172a",
                  padding: "12px 10px",
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                {menu}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </main>
    </>
  );
}
