# 자산도우미 PRD (Product Requirements Document)

> 버전: 1.0  
> 대상 단계: MVP → Beta  
> 부제: "내 소비가 키우는 또 하나의 나"
> 기준 문서: [자산도우미_아키텍처_옵션B.md](자산도우미_아키텍처_옵션B.md)의 권장안을 따른다. 초기 구현 기준은 Fly.io, Neon, APScheduler, Redis, Sentry다.

---

## 0. 문서 목적과 범위

본 문서는 [자산도우미_기획서.md](자산도우미_기획서.md)와 [자산도우미_아키텍처_옵션B.md](자산도우미_아키텍처_옵션B.md)에 기반해 **MVP 및 Beta 단계 개발의 단일 기준 문서(Single Source of Truth)** 를 제공합니다.

- **포함**: 사용자 스토리, 기능 명세, 인수조건(AC), 비기능 요구사항, 데이터 모델, API 개요, 테스트 시나리오(단위·통합·E2E)
- **제외**: 정식 단계(마이데이터 위탁) 전용 기능, 청소년 모드, 광고/BM 상세

---

## 1. 제품 개요

### 1-1. 비전
사회초년생이 결제 직전 한 박자 멈추고, 분신과 함께 자기 통제 습관을 만들도록 돕는 자산관리 동반자 앱.

### 1-2. 단계 정의
| 단계 | 데이터 소스 | 사용자 규모 가정 |
|---|---|---|
| **MVP** | 수동 입력 + 모의 데이터 | ~50명 베타 |
| **Beta** | 오픈뱅킹 잔액·이체 + (선택) 카드사 즉시알림 | ~1,000명 |

### 1-3. 1차 타깃
- 만 23~29세 사회초년생
- 월 가용 소득 50~250만 원
- 비상금/저축 목표는 있으나 추적 산발적
- 후불결제·구독 누수에 노출

### 1-4. 비목표 (Out of Scope)
- 전체 사용자 절대 자산 랭킹
- 실제 자산을 가상화폐 단위로 1:1 변환
- 자체 토큰 환금
- 청소년 단독 가입
- 밀리초 단위 실시간 푸시
- SMS 파싱 기반 결제 감지

---

## 2. 핵심 가치 제안

**"내 소비·저축 행동이 가상의 분신을 키우거나 시들게 한다 — 단, 사용자가 강도를 정한다."**

- 실제 자산 1:1 미러링 ❌ → 행동 결과를 추상화한 별도 지표(HP·성장도)
- 결제 직전·직후 "한 박자 멈춤" 모먼트
- 경쟁 ❌ → 자기 통제 + 선택적 동행
- 정신건강 가드레일: 강도/톤/빈도 사용자 조절, 비난 카피 금지

---

## 3. 사용자 스토리 (Epic & User Story)

### Epic 1: 분신 만들기
- **US-1.1** 사용자로서, 식물/캐릭터/도시/텍스트 중 하나의 분신을 선택할 수 있다.
- **US-1.2** 사용자로서, 시들기 시각효과 강도(1~3단계)를 직접 정할 수 있다.
- **US-1.3** 사용자로서, 분신 알림 일일 상한(N회)을 설정할 수 있다.

### Epic 2: 데이터 입력
- **US-2.1** (MVP) 사용자로서, 결제·저축·수입 내역을 수동으로 입력할 수 있다.
- **US-2.2** (MVP) 사용자로서, 모의 데이터 시드를 받아 체험할 수 있다.
- **US-2.3** (Beta) 사용자로서, 오픈뱅킹 OAuth로 본인 계좌를 연결할 수 있다.
- **US-2.4** (Beta) 사용자로서, 카드사 즉시알림 동의를 선택적으로 켤 수 있다.

### Epic 3: 분신 상태 (HP·성장도)
- **US-3.1** 사용자로서, 내 분신의 HP와 성장도를 대시보드에서 본다.
- **US-3.2** 사용자로서, 결제 이벤트가 분신에 미친 영향을 확인할 수 있다.
- **US-3.3** 사용자로서, HP 0이어도 비난적 표현 없이 회복 액션을 안내받는다.

### Epic 4: 멈춤 카드
- **US-4.1** 사용자로서, 일/주 누적금액·카테고리·시간대 임계를 설정할 수 있다.
- **US-4.2** 사용자로서, 임계 도달 시 웹 푸시로 멈춤 카드를 받는다.
- **US-4.3** 사용자로서, 큰 결제 전에 결제 시뮬레이터로 분신 영향을 미리 본다.
- **US-4.4** (Beta) 사용자로서, 카드사 즉시알림 직후 N초 회수창에서 "계획된 소비였나요?" 회고에 응답할 수 있다.

### Epic 5: 동행 기능
- **US-5.1** 사용자로서, 친구를 초대해 2~6명 소그룹 챌린지를 만들 수 있다.
- **US-5.2** 사용자로서, 친구 모집이 부담스러우면 봇 메이트와 함께할 수 있다.
- **US-5.3** 사용자로서, 과거 자아 비교를 켜고 끌 수 있으며 기본은 OFF다.
- **US-5.4** 사용자로서, 챌린지 목표를 절대 금액 대신 본인 평소 대비 % 변화로 설정할 수 있다.

### Epic 6: 학습·자동저축 (Beta 핵심)
- **US-6.1** 사용자로서, 1~2분짜리 학습 카드를 완료하면 분신 성장도가 +1된다.
- **US-6.2** (Beta) 사용자로서, 자동저축 룰을 만들 수 있다 (예: 월급일+1일에 10만원 이체).
- **US-6.3** (Beta) 사용자로서, 자동저축 룰 첫 실행 전 24시간 유예 동안 취소할 수 있다.
- **US-6.4** (Beta) 사용자로서, 자동저축 룰을 1탭으로 일시정지할 수 있다.
- **US-6.5** (Beta) 사용자로서, 잔액이 사용자 지정 하한 이하면 자동저축이 자동 일시정지된다.
- **US-6.6** (Beta) 사용자로서, 다음 자동저축 실행 결과를 시뮬레이션으로 미리 본다.

### Epic 7: 계정·동의
- **US-7.1** 사용자로서, 이메일/소셜 로그인으로 가입할 수 있다.
- **US-7.2** 사용자로서, 우울/강박 성향 자가체크를 선택적으로 수행할 수 있다.
- **US-7.3** 사용자로서, 언제든 메타포 OFF + 텍스트 모드로 전환할 수 있다.
- **US-7.4** 사용자로서, 데이터 다운로드/삭제를 요청할 수 있다.

---

## 4. 기능 명세 + 인수조건 (Acceptance Criteria)

> 표기법: Given / When / Then

### 4-1. 분신 HP 산식

**기능 정의**
- HP 범위: 0~100
- 매 시각 정각에 재계산 (Beta는 매 1시간, MVP는 매일)
- HP = 100 - 충동성 지수
- 충동성 지수 = `min(100, max(0, (최근 7일 일평균 결제액 / 사용자 베이스라인 - 1) * 100))`
- 베이스라인: 가입 후 첫 14일은 *기본값(사용자 자기보고 평균)*, 14일 이후는 직전 28일 일평균
- HP 변동 시각 효과 강도: 사용자 설정(1=부드러움, 3=자극적)

**인수조건 AC-HP-01**: 신규 가입자 HP 초기화
- *Given* 신규 가입한 사용자 (가입 후 0일)
- *When* 첫 분신을 선택
- *Then* HP는 100, 성장도는 0으로 초기화된다

**AC-HP-02**: 결제 발생 시 HP 즉시 반영
- *Given* HP 100, 베이스라인 일 30,000원인 사용자
- *When* 60,000원 결제 이벤트가 입력됨
- *Then* 즉시 재계산이 트리거되고 HP가 감소한다 (산식 검증)
- *And* `events` 테이블에 결제 이벤트가 1건 기록된다

**AC-HP-03**: HP 0에서 비난 카피 금지
- *Given* HP 0인 사용자
- *When* 대시보드를 연다
- *Then* 화면에 "실패", "당신은 X" 같은 비난 표현이 없다
- *And* 회복 액션 카드가 최소 1개 이상 노출된다

### 4-2. 멈춤 카드

**기능 정의**
- 트리거 3종
  1. 사전 임계 알림 (일/주 누적금액·카테고리·시간대)
  2. 결제 시뮬레이터 (사용자 능동 호출)
  3. (Beta) 카드사 즉시알림 후 N초 회수창
- 알림 빈도 상한: 사용자 설정 일 N회
- 발송 채널: 웹 푸시 (VAPID)

**AC-PAUSE-01**: 임계 도달 시 멈춤 카드 발송
- *Given* 일 누적 5만원 임계, 알림 일 상한 3회 설정 사용자
- *And* 오늘 누적 결제 4.5만원
- *When* 추가 1만원 결제가 입력됨
- *Then* 임계 초과로 웹 푸시가 발송된다
- *And* `notification_log`에 1건 기록된다

**AC-PAUSE-02**: 일 상한 초과 시 발송 중단
- *Given* 알림 일 상한 3회, 오늘 이미 3회 발송된 사용자
- *When* 4번째 임계 트리거가 발생
- *Then* 푸시는 발송되지 않는다
- *And* `notification_log`에 "suppressed_by_daily_cap" 사유로 기록된다

**AC-PAUSE-03**: 시뮬레이터 미리보기
- *Given* 사용자가 결제 시뮬레이터에 5만원 입력
- *When* "미리보기" 클릭
- *Then* 가상 HP 변동치가 화면에 표시된다
- *And* 실제 HP·이벤트 테이블은 수정되지 않는다

### 4-3. 자동저축 룰 (Beta)

**기능 정의**
- 룰 속성: 트리거(cron 표현식), 금액, 출금계좌, 입금계좌, 잔액 하한, 일시정지 여부
- 첫 실행 24시간 전 유예
- 잔액 < 하한이면 자동 일시정지
- 모든 실행/실패는 `auto_save_log`에 기록 (idempotency_key 포함)

**AC-AUTO-01**: 룰 생성 시 24시간 유예
- *Given* 사용자가 새 자동저축 룰을 생성
- *When* 룰의 다음 실행 시각이 23시간 후
- *Then* 룰 상태는 `pending_grace`로 저장된다
- *And* 24시간 경과 전까지는 실행되지 않는다
- *And* 사용자가 유예 기간 내 취소하면 룰은 `cancelled`로 전환되고 이체 발생 ❌

**AC-AUTO-02**: 잔액 하한 미달 시 자동 일시정지
- *Given* 잔액 하한 30만원, 잔액 25만원, 활성 룰 보유 사용자
- *When* 룰 실행 시점이 도래
- *Then* 이체는 시도되지 않는다
- *And* 룰 상태는 `auto_paused`로 변경된다
- *And* 사용자에게 알림이 1회 발송된다 (일 상한과 별도)
- *And* `auto_save_log`에 사유 `balance_below_threshold`로 기록된다

**AC-AUTO-03**: 멱등성 보장
- *Given* 동일 idempotency_key로 자동이체가 1회 성공
- *When* 같은 키로 재시도가 발생
- *Then* 외부 이체 API는 다시 호출되지 않는다
- *And* `auto_save_log`에 `duplicate_skipped`로 기록된다

**AC-AUTO-04**: 일시정지 1탭
- *Given* 활성 자동저축 룰이 있는 사용자
- *When* 일시정지 버튼을 1회 클릭
- *Then* 룰 상태는 즉시 `paused`로 변경된다
- *And* 다음 실행 시각이 도래해도 이체는 발생하지 않는다

### 4-4. 소그룹 챌린지

**AC-GROUP-01**: 인원 상한
- *Given* 6명이 참가한 챌린지
- *When* 7번째 사용자가 참가 시도
- *Then* 참가가 거부되고 "최대 인원 도달" 메시지가 표시된다

**AC-GROUP-02**: 우열 표시 금지
- *Given* 챌린지 룸에 5명 참가
- *When* 룸 화면을 연다
- *Then* 화면 어디에도 순위·랭킹·점수 비교 막대가 없다
- *And* 응원 버튼/메시지만 노출된다

**AC-GROUP-03**: 상대 % 목표
- *Given* 챌린지 목표 설정 화면
- *When* 사용자가 "절대 금액"을 선택 시도
- *Then* "본인 평소 대비 % 변화" 옵션이 권장되며 절대 금액은 보조 옵션으로 표시된다

### 4-5. 학습 카드

**AC-LEARN-01**: 학습 완료 시 성장도 +1
- *Given* 사용자가 학습 카드 1개를 시작
- *When* 카드를 끝까지 완료 (이수 조건 충족)
- *Then* 분신 성장도 +1
- *And* `learning_progress` 테이블에 완료 기록 1건

**AC-LEARN-02**: 동일 카드 중복 보상 방지
- *Given* 이미 완료한 학습 카드
- *When* 다시 완료
- *Then* 성장도는 증가하지 않는다 (단, 재학습 자체는 허용)

### 4-6. 계정·동의

**AC-ACCT-01**: 텍스트 모드 전환
- *Given* 분신 메타포 사용 중인 사용자
- *When* 설정에서 "텍스트 모드"를 켠다
- *Then* 모든 분신 시각요소가 텍스트로 대체된다
- *And* HP·성장도 산식과 데이터는 동일하게 유지된다

**AC-ACCT-02**: 데이터 삭제 요청
- *Given* 인증된 사용자
- *When* 계정 삭제를 요청하고 본인 확인을 완료
- *Then* 30일 내 모든 PII가 영구 삭제된다 (단, 법적 보관 의무 데이터 제외)
- *And* 삭제 작업은 감사 로그에 기록된다

### 4-7. 오픈뱅킹 연동 (Beta)

**AC-OB-01**: OAuth 동의 흐름
- *Given* Beta 사용자가 계좌 연결을 시도
- *When* 오픈뱅킹 OAuth 동의를 완료
- *Then* access_token이 저장(암호화)되고, 본인 보유 계좌 목록이 표시된다
- *And* refresh_token 만료 7일 전부터 갱신을 시도한다

**AC-OB-02**: Polling 빈도
- *Given* 활성 사용자
- *When* APScheduler가 5분 주기로 실행
- *Then* 마지막 polling 이후 5분 이상 경과한 사용자만 polling된다
- *And* 일별 호출 한도(예: 사용자당 200회)에 도달하면 다음날까지 stop

---

## 5. 비기능 요구사항 (NFR)

| 항목 | MVP 목표 | Beta 목표 |
|---|---|---|
| 응답 시간 (P95) | API < 500ms | API < 300ms |
| 가용성 | 95% | 99% |
| 동시 사용자 | 50 | 1,000 |
| 푸시 발송 지연 | 발송 시각 +30s | +10s |
| 데이터 백업 | 일 1회 | 일 2회 + PITR 7일 |
| 보안 | HTTPS 필수, OAuth token AES-256 암호화 저장 | + Rate limit, Sentry 모니터링 |
| 접근성 | 한국어, WCAG 2.1 AA 권장 | 동일 |
| 개인정보 | 최소 수집, 동의 분리 | + DPA, 30일 내 삭제 |

---

## 6. 시스템 아키텍처 요약

자세한 내용은 [자산도우미_아키텍처_옵션B.md](자산도우미_아키텍처_옵션B.md) 참조.

```
[Browser]
   │
   ▼
Next.js (Vercel)              ← 분신 UI, 웹 푸시 구독
   │ HTTPS (REST/JSON)
   ▼
FastAPI (Railway/Fly.io)      ← API + 인증 + 비즈니스 로직
   │
   ├─ APScheduler
   │     ├─ 매 5분: 오픈뱅킹 잔액 polling (Beta)
   │     ├─ 매시: 분신 HP 재계산
   │     └─ cron: 자동저축 룰 실행 (Beta)
   │
   ├─ SQLAlchemy 2.0 ──→ PostgreSQL (Neon/Supabase)
   └─ Web Push (pywebpush)
```

### 6-1. 스택 요약
- **Frontend**: Next.js 15 + TypeScript + Tailwind + Framer Motion
- **Backend**: Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 16
- **인증**: Authlib (OAuth) + 자체 JWT
- **푸시**: pywebpush (Web Push VAPID)
- **스케줄**: APScheduler
- **테스트**: pytest + pytest-asyncio (백엔드), Vitest + React Testing Library (프론트), Playwright (E2E)

---

## 7. 데이터 모델 (개요)

```
users               ─ id, email, password_hash, created_at, deleted_at
user_settings       ─ user_id, avatar_type, intensity, daily_alert_cap, text_mode, baseline_amount
avatars             ─ user_id, hp, growth, last_calculated_at
events              ─ id, user_id, type(payment|save|income|learn), amount, category, occurred_at, source(manual|openbanking)
thresholds          ─ user_id, kind(daily|weekly|category|time), value, category, time_window
notification_log    ─ id, user_id, kind, payload, sent_at, suppressed_reason
auto_save_rules     ─ id, user_id, cron, amount, src_account, dst_account, balance_floor, status, next_run_at, grace_until
auto_save_log       ─ id, rule_id, idempotency_key, status, reason, executed_at
groups              ─ id, name, max_members(2-6)
group_members       ─ group_id, user_id, joined_at
challenges          ─ id, group_id, target_type(percent|absolute), target_value, period
learning_cards      ─ id, title, body, duration_sec
learning_progress   ─ user_id, card_id, completed_at
oauth_tokens        ─ user_id, provider, access_token_enc, refresh_token_enc, expires_at
audit_log           ─ id, user_id, action, target, at, meta
```

핵심 제약:
- `events.idempotency_hash` UNIQUE (외부 결제 이벤트 중복 방지)
- `auto_save_log.idempotency_key` UNIQUE
- `oauth_tokens` 컬럼 AES-256 적용 (앱 레벨 암호화)

---

## 8. API 개요 (REST)

| Method | Path | 설명 | 인증 |
|---|---|---|---|
| POST | `/auth/signup` | 가입 | ❌ |
| POST | `/auth/login` | 로그인 | ❌ |
| GET | `/me` | 본인 정보 | ✅ |
| PATCH | `/me/settings` | 설정 변경 (강도/상한/텍스트모드) | ✅ |
| GET | `/avatar` | 분신 상태 조회 | ✅ |
| POST | `/events` | 이벤트 입력 (수동) | ✅ |
| POST | `/events/simulate` | 결제 시뮬레이션 | ✅ |
| GET | `/thresholds` `POST` `PATCH` `DELETE` | 임계 관리 | ✅ |
| POST | `/auto-save/rules` | 룰 생성 | ✅ |
| PATCH | `/auto-save/rules/:id` | 일시정지/재개 | ✅ |
| POST | `/auto-save/rules/:id/cancel` | 유예 중 취소 | ✅ |
| GET | `/auto-save/rules/:id/preview` | 다음 실행 시뮬레이션 | ✅ |
| POST | `/groups` `GET` | 챌린지 그룹 | ✅ |
| POST | `/groups/:id/members` | 참가 (인원 6 초과 시 422) | ✅ |
| GET | `/learning/cards` | 카드 목록 | ✅ |
| POST | `/learning/cards/:id/complete` | 완료 보고 | ✅ |
| POST | `/openbanking/connect` (Beta) | OAuth 콜백 처리 | ✅ |
| POST | `/push/subscribe` | 웹 푸시 구독 등록 | ✅ |
| POST | `/account/delete` | 계정 삭제 요청 | ✅ |

응답 표준: JSON, 에러는 `{ "error": { "code": "...", "message": "..." } }` 포맷.

---

## 9. 테스트 전략

### 9-1. 테스트 피라미드 목표

| 레벨 | 비중 | 도구 |
|---|---|---|
| 단위 테스트 | 70% | pytest, Vitest |
| 통합 테스트 | 20% | pytest + httpx + Testcontainers (Postgres) |
| E2E 테스트 | 10% | Playwright |

### 9-2. 단위 테스트 (Unit Tests)

**대상**: 순수 함수, 도메인 로직, 컴포넌트 단위

#### Backend (pytest)

- **UT-HP-01** `calculate_hp(events, baseline)` 충동성 지수 산식
  - 베이스라인 동일 → HP 100
  - 평소 2배 결제 → HP ≤ 0 (clamp 검증)
  - 결제 0건 → HP 100
  - 베이스라인 0이거나 None → 기본 베이스라인 사용 (ZeroDivisionError 미발생)

- **UT-HP-02** `should_calculate(last_calculated_at, now)` 1시간 주기 검증
  - 59분 경과 → False
  - 60분 경과 → True

- **UT-PAUSE-01** `is_threshold_exceeded(events, threshold)`
  - 일 누적 임계 검증 (시간대·카테고리 조합)
  - 시간대 외 결제는 합산 제외
  - 카테고리 미스매치는 제외

- **UT-PAUSE-02** `should_suppress_alert(user, today_count)` 일 상한 검증
  - 상한 도달 → True
  - 상한 미달 → False
  - 상한 0 (알림 OFF) → 항상 True

- **UT-AUTO-01** `is_within_grace(rule, now)` 24시간 유예
  - grace_until > now → True
  - grace_until ≤ now → False

- **UT-AUTO-02** `should_auto_pause(rule, balance)` 잔액 하한
  - balance < floor → True
  - balance == floor → False (경계값)

- **UT-AUTO-03** `make_idempotency_key(rule_id, scheduled_at)` 결정론
  - 같은 입력 → 같은 키
  - rule_id 변경 → 다른 키

- **UT-COPY-01** `validate_copy(text)` 비난 카피 차단
  - "실패", "당신은 X" 포함 → ValidationError 발생
  - 정상 카피 → 통과

- **UT-GROUP-01** `can_join_group(group, user)` 인원 상한
  - 5명 + 신규 1명 → True
  - 6명 + 신규 1명 → False

#### Frontend (Vitest + RTL)

- **UT-FE-01** `<HpBar />` 컴포넌트
  - props.hp=0일 때 비난 텍스트 미렌더링
  - 회복 액션 CTA 표시

- **UT-FE-02** `<IntensitySlider />` 1~3단계만 허용

- **UT-FE-03** `<TextModeProvider />` 켜진 상태에서 분신 SVG가 텍스트로 치환

- **UT-FE-04** `<SimulatorForm />` 미리보기 결과가 실제 HP API를 호출하지 않음 (mock 검증)

### 9-3. 통합 테스트 (Integration Tests)

**대상**: API + DB + 외부 모듈 mock 조합

도구: pytest + httpx AsyncClient + Testcontainers PostgreSQL

- **IT-EVT-01** `POST /events` 결제 입력 → DB 기록 + HP 재계산 트리거
  - DB에 events row 1건
  - avatars.hp 즉시 갱신
  - notification_log에 임계 초과 시 기록

- **IT-EVT-02** 동일 idempotency_hash 중복 입력 → 409 Conflict, DB 중복 없음

- **IT-AUTO-01** `POST /auto-save/rules` 생성 → status=pending_grace, grace_until=now+24h

- **IT-AUTO-02** APScheduler가 grace_until 도달 전 실행 시도 → 이체 mock 호출 0회

- **IT-AUTO-03** 잔액 하한 미달 시뮬레이션 → status=auto_paused, log 1건

- **IT-AUTO-04** 동일 idempotency_key로 2회 호출 → 외부 이체 API mock 1회만 호출

- **IT-PUSH-01** 임계 초과 → pywebpush mock 1회 호출, notification_log 1건

- **IT-PUSH-02** 일 상한 초과 시 → pywebpush mock 호출 0회, log에 suppressed_by_daily_cap

- **IT-OB-01** (Beta) OAuth 콜백 처리 → oauth_tokens에 암호화 저장 (raw 평문 저장 안 됨 검증)

- **IT-OB-02** (Beta) Polling 작업이 마지막 polling +5분 미만 사용자는 skip

- **IT-GROUP-01** `POST /groups/:id/members` 7번째 참가 → 422 + "max_members_reached"

- **IT-LEARN-01** 동일 카드 2회 완료 → 성장도 +1만 발생

- **IT-DEL-01** `POST /account/delete` → audit_log 기록 + 30일 후 PII soft delete 작업 큐 등록

### 9-4. E2E 테스트 (Playwright)

**대상**: 실제 브라우저에서의 사용자 시나리오 (Frontend + Backend + DB 통합)

#### MVP 시나리오

- **E2E-01** 신규 가입 → 분신 선택 → 강도 설정 → 대시보드 진입
  1. `/signup` 이메일 가입
  2. 분신 "식물" 선택, 강도 "1" 선택
  3. 대시보드 HP=100, 성장도=0 표시 확인

- **E2E-02** 수동 결제 입력 → HP 감소
  1. 로그인 (베이스라인 30,000원 사용자 시드)
  2. 60,000원 결제 입력
  3. 대시보드 새로고침 후 HP가 100보다 낮음
  4. 비난 카피 미존재 검증

- **E2E-03** 임계 설정 → 멈춤 카드 푸시
  1. 일 누적 5만원 임계 설정
  2. 4.5만원 → 1만원 결제 입력
  3. 푸시 알림 수신 mock 확인 (Service Worker)
  4. 알림 클릭 시 회고 화면 노출

- **E2E-04** 결제 시뮬레이터
  1. 시뮬레이터 페이지 진입
  2. 5만원 입력 → 미리보기
  3. 가상 HP 표시, 실제 HP는 변동 없음 (DB 검증)

- **E2E-05** 텍스트 모드 전환
  1. 설정 → 텍스트 모드 ON
  2. 대시보드에 분신 SVG 없음, 텍스트만 노출
  3. HP 수치는 동일

- **E2E-06** 학습 카드 완료 → 성장도 +1
  1. 카드 1개 끝까지 시청
  2. 완료 버튼 클릭
  3. 성장도 1 증가 확인

- **E2E-07** 소그룹 챌린지 생성·참가
  1. 사용자 A가 그룹 생성 (max=4)
  2. 사용자 B, C, D 참가 (총 4명)
  3. 사용자 E 참가 시도 → "최대 인원" 에러
  4. 룸 화면에 순위·점수 비교 UI 미존재

#### Beta 시나리오 (추가)

- **E2E-08** 오픈뱅킹 OAuth 연결 (mock 서버)
  1. "계좌 연결" 클릭
  2. mock OAuth 동의 페이지에서 승인
  3. 콜백 후 보유 계좌 목록 표시
  4. DB에 암호화된 토큰 저장 확인

- **E2E-09** 자동저축 룰 생성 → 24시간 유예 → 취소
  1. 룰 생성 (월급일+1일 10만원)
  2. 상태 `pending_grace` 표시
  3. 유예 기간 내 취소
  4. 이체 발생하지 않음 확인 (auto_save_log 비어있음)

- **E2E-10** 자동저축 일시정지 1탭
  1. 활성 룰의 일시정지 버튼 클릭
  2. 즉시 상태 `paused`로 표시
  3. 다음 cron tick에서 이체 시도 안 됨

- **E2E-11** 잔액 하한 미달 자동 일시정지
  1. 잔액 하한 30만원 룰, 모의 잔액 25만원으로 설정
  2. cron tick 트리거
  3. 룰 상태 `auto_paused`, 알림 1회

### 9-5. 수동 검증 항목 (Exploratory)

자동화가 어렵거나 비용 대비 효율이 낮은 영역:

- **MV-01** 분신 시각효과 강도 1~3단계의 정서적 적절성 (사용자 인터뷰)
- **MV-02** 비난 카피 정책 — 카피 라이팅 회의에서 검수
- **MV-03** 푸시 알림 톤·문구 — 실제 디바이스에서 수신 시 위화감 검토
- **MV-04** 접근성 — 스크린리더, 키보드 네비게이션
- **MV-05** 다크모드/라이트모드 일관성

### 9-6. CI/CD 파이프라인 게이트

| 단계 | 통과 조건 |
|---|---|
| PR open | 단위 테스트 100% 통과, 커버리지 ≥ 80% |
| PR merge to main | 단위 + 통합 테스트 100% 통과 |
| Staging 배포 후 | E2E 시나리오 전체 통과 |
| Production 배포 전 | 수동 검증 체크리스트 + 보안 스캔 (Bandit, npm audit) |

---

## 10. 출시 기준 (Definition of Done)

### MVP 출시 가능 조건
- [ ] Epic 1, 2(US-2.1·2.2), 3, 4(US-4.1·4.2·4.3), 5, 6(US-6.1만), 7(US-7.1·7.3) 완료
- [ ] AC-HP-*, AC-PAUSE-01·02·03, AC-GROUP-*, AC-LEARN-*, AC-ACCT-01 모두 통과
- [ ] 단위 + 통합 + MVP E2E 시나리오 통과
- [ ] 비기능 요구 MVP 목표 충족
- [ ] 개인정보 처리방침·이용약관 게시

### Beta 출시 가능 조건
- [ ] MVP 모든 조건 + Epic 2(US-2.3·2.4), 6(US-6.2~6.6), 7(US-7.4) 완료
- [ ] AC-AUTO-*, AC-OB-* 통과
- [ ] Beta E2E 시나리오 통과
- [ ] 비기능 요구 Beta 목표 충족
- [ ] 오픈뱅킹 사업자 운영 환경 키 확보 및 보안 검토 완료

---

## 11. 리스크와 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| 분신 메타포 거부감 | 핵심 UX 실패 | 텍스트 모드 + 다중 메타포 (Epic 7) |
| 정신건강 부담 | 평판·법적 리스크 | 가드레일 정책, 자가체크 옵션, 비난 카피 금지 자동 검증(UT-COPY-01) |
| 자동저축 사용자 실수 | 금전적 손해 | 24시간 유예 + 잔액 하한 + 1탭 정지 (AC-AUTO-*) |
| 오픈뱅킹 호출 한도 | 서비스 정지 | Polling 조건부 + 일별 한도 모니터링 (AC-OB-02) |
| 그룹 사회적 압력 | 사용자 이탈 | % 기반 목표 권장, 우열 표시 금지 (AC-GROUP-02·03) |

---

## 12. 부록

### 12-1. 용어 정의
- **HP**: 분신 체력. 0~100. 최근 7일 충동성 지수의 역수
- **성장도**: 누적 저축·학습·자동이체 이행의 일관성 점수
- **베이스라인**: 사용자 본인의 평소 일평균 결제액
- **멈춤 카드**: 결제 결정 직전·직후의 의식적 점검을 유도하는 푸시·UI 요소
- **그레이스(grace)**: 자동저축 룰 첫 실행 전 24시간 취소 가능 기간

### 12-2. 의도적 제외 (Non-Goals 재확인)
- 전체 사용자 절대 자산 랭킹
- 실제 자산 1:1 가상화폐 변환
- 자체 토큰 환금
- 청소년 단독 가입
- 밀리초 단위 실시간 푸시
- SMS 파싱 결제 감지

### 12-3. 참고 문서
- [자산도우미_기획서.md](자산도우미_기획서.md)
- [자산도우미_아키텍처_옵션B.md](자산도우미_아키텍처_옵션B.md)
