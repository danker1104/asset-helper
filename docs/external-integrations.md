# 외부 연동 API 정리

이 문서는 실제 외부 서비스 연동 시 필요한 API와 현재 앱이 기대하는 경계를 정리합니다.

## 1. 오픈뱅킹

### 필요한 API
- OAuth authorization endpoint
- OAuth token exchange endpoint
- OAuth token refresh endpoint
- 계좌 목록 조회 API
- 잔액 조회 API
- 거래 내역 조회 API

### 현재 앱에서의 사용 위치
- `/openbanking/connect`
- `/openbanking/poll`
- `/openbanking/refresh`

### 필요한 데이터
- access token
- refresh token
- token expiry
- account id
- account name
- balance
- 거래 시각

## 2. 웹 푸시

### 필요한 API
- 브라우저 PushManager 구독 생성
- VAPID 기반 push send API

### 현재 앱에서의 사용 위치
- `/push/subscribe`

### 필요한 데이터
- endpoint
- `p256dh`
- `auth`

## 3. 카드사 즉시알림 연동

### 필요한 API
- 알림 수신 webhook
- 알림 검증 서명/토큰 확인 API
- 알림 재전송 대비 idempotency 처리

### 현재 앱에서의 사용 위치
- PRD 상 카드사 즉시알림 회수창 기능

### 필요한 데이터
- 알림 식별자
- 사용자 식별자
- 승인 금액
- 승인 시각
- 가맹점/카테고리 정보

## 4. 계정 인증

### 필요한 API
- 로그인
- 세션 발급
- 토큰 검증
- 계정 삭제 요청

### 현재 앱에서의 사용 위치
- `/auth/signup`
- `/auth/login`
- `/account/delete`

## 5. 구현 메모

- 외부 연동은 먼저 내부 API 계약을 고정한 뒤, provider adapter를 분리하는 방식이 안전합니다.
- 실서비스 전환 시에는 각 provider에 대한 retry, timeout, circuit breaker, idempotency key를 별도로 둬야 합니다.
