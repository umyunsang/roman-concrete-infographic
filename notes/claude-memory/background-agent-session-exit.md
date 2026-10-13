---
name: background-agent-session-exit
description: 세션 종료로 끊긴 백그라운드 서브에이전트는 SendMessage로 재개될 수도, 거부될 수도 있음 — 긴 에이전트는 중간 결론·진행을 파일로 남기게 할 것
metadata:
  type: feedback
---

세션이 끝날 때 돌던 백그라운드 서브에이전트를 SendMessage로 다시 부르면 결과가 둘로 갈린다.

- **재개됨:** 워커 3명(W1~W3)은 2026-10-01 03:50에 세션 종료로 끊겼는데, SendMessage를 보내자 정상적으로 이어서 작업했다.
- **거부됨:** 1라운드 심사 에이전트는 "stopped by the user and won't be resumed"로 거부됐다. 이 경우 새 에이전트는 사용자가 명시적으로 요청할 때만 띄울 수 있다.
- **thinking은 남지 않는다:** 트랜스크립트에는 thinking이 빈 문자열로 저장된다. 따라서 파일에 적지 않은 결론은 복구할 수 없다.

**Why:** 심사 에이전트가 확대컷 70여 장을 보고도 결론을 파일에 남기지 않았다. 그 상태에서 재개가 거부되어 작업을 통째로 잃었고, 감독이 직접 다시 심사해야 했다([[colosseum-poster-mindmap]]).

**How to apply:**
- 오래 걸리는 심사·분석·워커 에이전트의 지시문에 "항목 하나 끝날 때마다 중간 결론이나 진행 내용을 REPORT·progress 파일에 덧붙일 것"을 넣는다.
- 루프의 상태 파일(STATE.md)에 에이전트 ID와 다음 단계를 적어 둔다.
- 세션을 재개하면 먼저 SendMessage로 재개를 시도한다. 거부되면 사용자의 계속 진행 지시를 근거로 새 에이전트를 띄운다.
