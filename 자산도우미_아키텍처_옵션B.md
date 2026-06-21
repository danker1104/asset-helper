# 자산도우미 아키텍처 — 옵션 B (MVP → Beta)

> FastAPI(Python) + Next.js(TypeScript) 기반 경량 풀스택 구성
> 이 문서는 아래 권장안을 기준으로 작성하며, 초기 구현 선택지는 다음으로 고정한다: Fly.io, Neon, APScheduler, Redis, Sentry.

---

## 1. 한눈에 보는 다이어그램

```
[Browser]
   │
   ▼
Next.js (Vercel)              ← 분신 UI, 웹 푸시 구독
   │ HTTPS (REST/JSON)
   ▼
FastAPI (Railway/Fly.io)      ← API + 인증 + 비즈니스 로직
   │
  ├─ APScheduler (동일 프로세스 워커)
   │     ├─ 매 5분: 오픈뱅킹 잔액 polling
   │     ├─ 매시: 분신 HP 재계산
   │     └─ cron: 자동저축 룰 실행
   │
   ├─ SQLAlchemy 2.0 ──→ PostgreSQL (Neon / Supabase / Railway)
   └─ Web Push (pywebpush) — 멈춤 카드 발송
```

---

## 2. 확정 근거 (MVP/Beta 한정)

1. **컴포넌트가 4개**(웹·API·DB·푸시) — 운영 인력 1~2명으로 충분
2. **Redis·Celery 없이** APScheduler로 스케줄·polling 처리 가능 (Beta 트래픽 수준에서 충분)
3. 정식 단계로 갈 때 Celery + Redis만 *나중에 끼워 넣어도* 큰 재작성 없음
4. 금융 분석은 가볍게 시작해도 됨 — Python은 초기 백엔드 표준 언어로 고정하고 추후 분석 모듈 확장에도 그대로 사용
5. 분신 HP·충동성 지수는 pandas/numpy로 자연스러움, 데이터 검증은 Pydantic 내장

---

## 3. 단계별 컴포넌트 추가

| 시점 | 추가 컴포넌트 | 이유 |
|---|---|---|
| MVP 시작 | Next.js + FastAPI + PostgreSQL | 기본 |
| 멈춤 카드 도입 | Web Push (pywebpush) | 푸시 전용 외부 서비스 없이 표준 사용 |
| Beta 진입 | APScheduler / cron 잡 | 자동저축·polling |
| Beta 트래픽 증가 | Redis (캐시 + rate limit) | 오픈뱅킹 호출 한도 보호 |
| Beta 후반 (검토) | Celery 도입 검토 | 자동이체 실패 재시도가 잦아지면 |

---

## 4. 권장 스택

```yaml
Frontend:
  - Next.js 15 (App Router)
  - TypeScript
  - Tailwind CSS
  - Framer Motion       # 분신 애니메이션
  - 호스팅: Vercel

Backend:
  - Python 3.12
  - FastAPI + Pydantic v2
  - SQLAlchemy 2.0 (async)
  - Alembic (마이그레이션)
  - Authlib (OAuth - 오픈뱅킹)
  - pywebpush (멈춤 카드)
  - APScheduler (Beta 스케줄)
  - 호스팅: Fly.io

Database:
  - PostgreSQL 16
  - 호스팅: Neon

Beta 추가 (검토 순서):
  - Redis (Upstash) — polling rate limit, 세션 캐시
  - Sentry — 에러 추적
  - PostHog — 사용자 행동 분석 (KPI 측정, 실제 유입 후)
```

---

## 5. 예상 월 비용 (MVP~Beta 초기)
- Vercel Hobby: $0
- Railway/Fly.io: $5~20
- Neon/Supabase: $0~25
- Sentry/PostHog: $0 (무료 티어)
- **합계: $5~50/월**

Beta 사용자 1,000명 수준까지 이 구성으로 충분.

---

## 6. 옵션 A(Next.js 풀스택)와의 비교

| 항목 | 옵션 A 풀스택 | 옵션 B 경량 (이 문서) |
|---|---|---|
| MVP 속도 | 더 빠름 | 살짝 느림 |
| 자동저축 룰 (Beta) | BullMQ + Node 워커 별도 호스팅 필요 | APScheduler로 단일 프로세스 |
| 오픈뱅킹 OAuth | 라이브러리 선택지 적음 | Authlib 검증된 표준 |
| HP 베이스라인 계산 (충동성 지수) | JS로 직접 또는 별도 마이크로서비스 | pandas/numpy 자연스러움 |
| 데이터 검증 | Zod 등 별도 도구 | Pydantic 내장 |
| 향후 확장 | 분석 강화 시 Python 추가 필요 → 두 언어 강제 | 처음부터 Python이라 일관 |

→ Beta까지 가면 옵션 A도 결국 Node 워커 + 별도 호스팅 + 분석용 Python 마이크로서비스 형태로 흘러갈 가능성이 큼. 그러면 컴포넌트 수는 비슷해지면서 언어만 두 개가 됨.

---

## 7. 정식 단계로 갈 때 변경 사항 (참고용)

- APScheduler → **Celery + Redis** (재시도·idempotency 강화)
- 단일 DB → **이벤트 로그 테이블 추가** (감사용)
- Fly.io → **Cloud Run** (스케일링)
- 마이데이터 사업자 위탁 모듈 추가

이 전환은 *코드 재작성*이 아니라 *컴포넌트 추가*에 가까워 부담이 적음.
