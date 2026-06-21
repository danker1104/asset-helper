"use client";

import { useEffect, useMemo, useState } from "react";

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

const menuTabs: MenuTab[] = ["주식", "홈", "미션", "랭킹"];

const initialCompanies: StockCompany[] = [
  { symbol: "MTR", name: "메타리테일", price: 48500, drift: 0.08, volatility: 0.9, liquidity: 5200, lastChange: 0, orderPressure: 0 },
  { symbol: "GEX", name: "그린에너지X", price: 73200, drift: 0.11, volatility: 1.3, liquidity: 3300, lastChange: 0, orderPressure: 0 },
  { symbol: "NCS", name: "뉴클라우드솔루션", price: 118000, drift: 0.14, volatility: 1.7, liquidity: 2400, lastChange: 0, orderPressure: 0 },
  { symbol: "HFB", name: "헬스바이오랩", price: 35600, drift: 0.05, volatility: 1.5, liquidity: 4100, lastChange: 0, orderPressure: 0 },
  { symbol: "LGT", name: "로지텍모빌리티", price: 92400, drift: 0.09, volatility: 1.1, liquidity: 2900, lastChange: 0, orderPressure: 0 },
];

const dailyMissionPool = [
  "비상금 통장에 1,000원 이상 저축하기",
  "오늘 소비 내역 3건 기록하기",
  "충동구매 후보 상품 1개를 24시간 보류하기",
  "금융 학습 카드 1개 완료하기",
  "구독 서비스 1개 점검하기",
  "오늘 소비 중 가장 만족한 지출 기록하기",
  "오늘 소비 중 가장 후회되는 지출 기록하기",
  "목표 저축 진행률 확인하기",
  "편의점 지출 5,000원 이하로 유지하기",
  "외식 대신 집에서 한 끼 해결하기",
  "하루 동안 음료 구매하지 않기",
  "계좌 잔액 확인하기",
  "소비 전 10초 멈춤 실천하기",
  "장바구니 상품 1개 삭제하기",
  "지출 카테고리 3개 분류하기",
  "자동저축 설정 확인하기",
  "절약할 수 있는 소비 1개 찾기",
  "예상 지출 1개 미리 기록하기",
  "무지출 시간 6시간 달성하기",
  "친구 또는 가족에게 소비 습관 목표 공유하기",
  "오늘 소비를 한 문장으로 요약하기",
  "할인이나 쿠폰 1개 활용하기",
  "비상금 목표 금액 다시 확인하기",
  "분신 회복 행동 1회 수행하기",
  "금융 상식 퀴즈 3문제 풀기",
  "가계부 연속 출석하기",
  "오늘 필요 소비와 욕구 소비 구분하기",
  "저축 목표 이유 다시 읽어보기",
  "소비 일기 100자 이상 작성하기",
  "하루 마무리 소비 점검하기",
];

const weeklyMissionPool = [
  "일주일 동안 소비 기록 빠짐없이 작성하기",
  "무지출 데이 2일 달성하기",
  "비상금 1만 원 이상 모으기",
  "저축 목표 진행률 5% 올리기",
  "금융 학습 카드 5개 완료하기",
  "충동구매 3회 이상 참기",
  "정기 구독 서비스 전체 점검하기",
  "외식 횟수 줄이기",
  "소비 일기 5일 이상 작성하기",
  "예산 범위 내에서 한 주 보내기",
  "후회 소비 2건 이하 달성하기",
  "자동저축 규칙 1개 만들기",
  "생활비 절약 방법 3개 실천하기",
  "지출 카테고리 분석 완료하기",
  "예상 지출과 실제 지출 비교하기",
  "비상금 목표의 10% 달성하기",
  "분신 HP 80 이상 유지하기",
  "분신 성장도 5단계 올리기",
  "계획 소비 비율 80% 이상 달성하기",
  "주간 소비 리포트 작성하기",
];

const randomMissionPool = [
  "24시간 동안 장바구니 비우기",
  "오늘 저축하면 경험치 2배 받기",
  "소비 일기 작성 시 보상 2배",
  "친구에게 응원 보내기",
  "과거 소비 패턴 확인하기",
  "금융 퀴즈 만점 도전하기",
  "3일 연속 출석하기",
  "저축 목표 이름 새로 정하기",
  "이번 달 절약 금액 계산하기",
  "필요 없는 앱 1개 삭제하기",
  "냉장고 재료만으로 한 끼 해결하기",
  "오늘 카페 지출 없이 보내기",
  "가장 비싼 소비 분석하기",
  "한 주 소비 목표 재설정하기",
  "미래의 나에게 소비 다짐 남기기",
  "목표 달성 스크린샷 남기기",
  "지출 상위 카테고리 확인하기",
  "비상금 챌린지 참여하기",
  "분신 성장 스토리 확인하기",
  "일주일 목표를 친구와 공유하기",
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

function estimateExecutionPrice(company: StockCompany, qty: number, side: "buy" | "sell") {
  const impactRatio = qty / company.liquidity;
  return Math.max(
    100,
    Math.round(company.price * (1 + (side === "buy" ? 1 : -1) * impactRatio * 0.35)),
  );
}

function calculateHp(amount: number, baseline: number) {
  const safeBaseline = baseline > 0 ? baseline : 30000;
  const impulseIndex = Math.max(0, Math.min(100, (amount / safeBaseline - 1) * 100));
  return Math.max(0, Math.min(100, Math.round(100 - impulseIndex)));
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
  const [amount, setAmount] = useState("60000");
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
      const response = await fetch(`${apiBaseUrl}/missions/ranking?limit=20`);
      const body = await response.json();
      if (!response.ok) {
        setMissionRanking([]);
        return;
      }

      setMissionRanking(Array.isArray(body?.items) ? body.items : []);
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

  useEffect(() => {
    if (activeTab !== "랭킹" || !isLoggedIn) {
      setMyMissionRank(null);
      return;
    }

    loadMissionRanking();
    loadMyMissionRank();
  }, [activeTab, currentUserId, isLoggedIn]);

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

  const onCalculate = () => {
    setHp(calculateHp(Number(amount), Number(baseline)));
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
      setLoggedInNickname(nickname);
      setIsAuthPanelOpen(false);
      setLoginMessage(`로그인 성공: ${body.user_id}`);
    } catch {
      setLoginMessage("로그인 중 오류가 발생했습니다.");
    }
  };

  return (
    <main
      style={{
        maxWidth: 960,
        margin: "0 auto",
        padding: "64px 24px 140px",
      }}
    >
      {activeTab === "홈" ? (
      <section
        style={{
          background: "rgba(255,255,255,0.78)",
          border: "1px solid rgba(148,163,184,0.22)",
          borderRadius: 24,
          boxShadow: "0 24px 80px rgba(15,23,42,0.08)",
          padding: 32,
          backdropFilter: "blur(12px)",
        }}
      >
        <p style={{ margin: 0, fontSize: 14, color: "#475569" }}>MVP 첫 슬라이스</p>
        <h1 style={{ margin: "8px 0 12px", fontSize: 44, lineHeight: 1.1 }}>
          내 소비가 키우는 또 하나의 나
        </h1>
        <p style={{ margin: 0, maxWidth: 720, fontSize: 18, lineHeight: 1.6, color: "#334155" }}>
          수동 결제 입력으로 분신 HP 변화를 바로 확인하는 화면입니다. 불필요한 기능은 빼고 핵심만 남겼습니다.
        </p>

        {isLoggedIn ? (
          <p
            aria-label="logged-in-nickname"
            style={{
              margin: "18px 0 0",
              display: "inline-flex",
              alignItems: "center",
              borderRadius: 999,
              background: "#fee2e2",
              color: "#991b1b",
              padding: "10px 16px",
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            {loggedInNickname} 님
          </p>
        ) : (
          <button
            type="button"
            aria-label="auth-panel-toggle"
            onClick={() => setIsAuthPanelOpen((prev) => !prev)}
            style={{
              marginTop: 18,
              border: "none",
              borderRadius: 999,
              background: "#dc2626",
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
            {isLoggedIn ? null : (
              <label style={{ display: "grid", gap: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 600 }}>이메일</span>
                <input
                  aria-label="email-input"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  style={{
                    borderRadius: 14,
                    border: "1px solid #cbd5e1",
                    padding: "14px 16px",
                    fontSize: 16,
                  }}
                />
              </label>
            )}

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

            {isLoggedIn ? null : (
              <label style={{ display: "flex", alignItems: "center", gap: 10, paddingTop: 30 }}>
                <input
                  aria-label="text-mode-toggle"
                  type="checkbox"
                  checked={textMode}
                  onChange={(event) => setTextMode(event.target.checked)}
                />
                <span style={{ fontSize: 14, fontWeight: 600 }}>텍스트 모드</span>
              </label>
            )}
          </div>

          <div style={{ marginTop: 18, fontSize: 14, color: "#475569" }} data-testid="onboarding-summary">
            {isLoggedIn ? `${avatarType} · 강도 ${intensity}` : `${email} · ${avatarType} · 강도 ${intensity} · ${textMode ? "텍스트 모드" : "메타포 모드"}`}
          </div>

        </div>

        {isAuthPanelOpen ? (
          <div
            style={{
              marginTop: 24,
              padding: 20,
              borderRadius: 20,
              background: "#fff7ed",
              border: "1px solid #fed7aa",
            }}
          >
            <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "#9a3412" }}>인증</p>
            <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
              <button
                type="button"
                onClick={() => setAuthView("signup")}
                style={{
                  border: authView === "signup" ? "none" : "1px solid #fdba74",
                  borderRadius: 999,
                  background: authView === "signup" ? "#9a3412" : "white",
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
                onClick={() => setAuthView("login")}
                style={{
                  border: authView === "login" ? "none" : "1px solid #fdba74",
                  borderRadius: 999,
                  background: authView === "login" ? "#9a3412" : "white",
                  color: authView === "login" ? "white" : "#9a3412",
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
                      style={{ borderRadius: 14, border: "1px solid #fdba74", padding: "14px 16px", fontSize: 16 }}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600 }}>회원가입 비밀번호</span>
                    <input
                      aria-label="signup-password"
                      type="password"
                      value={signupPassword}
                      onChange={(event) => setSignupPassword(event.target.value)}
                      style={{ borderRadius: 14, border: "1px solid #fdba74", padding: "14px 16px", fontSize: 16 }}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600 }}>회원가입 닉네임</span>
                    <input
                      aria-label="signup-nickname"
                      value={signupNickname}
                      onChange={(event) => setSignupNickname(event.target.value)}
                      style={{ borderRadius: 14, border: "1px solid #fdba74", padding: "14px 16px", fontSize: 16 }}
                    />
                  </label>
                </div>

                <button
                  type="button"
                  aria-label="signup-submit"
                  onClick={onSignup}
                  style={{ marginTop: 16, border: "none", borderRadius: 999, background: "#9a3412", color: "white", padding: "12px 18px", fontSize: 15, fontWeight: 700, cursor: "pointer" }}
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
                      style={{ borderRadius: 14, border: "1px solid #fdba74", padding: "14px 16px", fontSize: 16 }}
                    />
                  </label>
                  <label style={{ display: "grid", gap: 8 }}>
                    <span style={{ fontSize: 14, fontWeight: 600 }}>로그인 비밀번호</span>
                    <input
                      aria-label="login-password"
                      type="password"
                      value={loginPassword}
                      onChange={(event) => setLoginPassword(event.target.value)}
                      style={{ borderRadius: 14, border: "1px solid #fdba74", padding: "14px 16px", fontSize: 16 }}
                    />
                  </label>
                </div>

                <button
                  type="button"
                  aria-label="login-submit"
                  onClick={onLogin}
                  style={{ marginTop: 14, border: "1px solid #9a3412", borderRadius: 999, background: "white", color: "#9a3412", padding: "12px 18px", fontSize: 15, fontWeight: 700, cursor: "pointer" }}
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
        ) : null}

        {/* HP 계산 입력 */}
        <div
          style={{
            display: "grid",
            gap: 16,
            marginTop: 20,
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          }}
        >
          <label style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 600 }}>평소 일평균 결제액</span>
            <input
              aria-label="baseline-input"
              value={baseline}
              onChange={(event) => setBaseline(event.target.value)}
              inputMode="numeric"
              style={{
                borderRadius: 14,
                border: "1px solid #cbd5e1",
                padding: "14px 16px",
                fontSize: 16,
              }}
            />
          </label>

          <label style={{ display: "grid", gap: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 600 }}>이번 결제 금액</span>
            <input
              aria-label="amount-input"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              inputMode="numeric"
              style={{
                borderRadius: 14,
                border: "1px solid #cbd5e1",
                padding: "14px 16px",
                fontSize: 16,
              }}
            />
          </label>
        </div>

        <button
          type="button"
          onClick={onCalculate}
          style={{
            marginTop: 20,
            border: "none",
            borderRadius: 999,
            background: "#0f172a",
            color: "white",
            padding: "14px 20px",
            fontSize: 16,
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          HP 계산하기
        </button>

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
  );
}
