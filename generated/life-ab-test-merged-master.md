# 이직 vs 현재 회사 잔류

## 1. 제품 한 줄 정의
사용자의 선택지 A/B를 동일 baseline 위에서 시뮬레이션해 비교하는 인생 AB 테스트 게임

## 2. 입력 정규화 및 기본 가정
- user_profile이 없어 기본 프로필을 적용했다.

## 3. Topline verdict
이직한다가 현재 가정에서는 평균 1점 우세하다. 단, 이 결과는 정답이 아니라 조건부 우세이며 리스크와 후회 구조를 함께 봐야 한다.

## 4. 누구에게 어떤 조건에서 A/B가 맞는가
- 사용자가 중요하다고 지정한 must_consider(재정 안정, 성장 속도) 축을 우선 반영해 비교했다.
- 성장/실력 축적은 현재 회사에 남는다 쪽이 더 유리하다.
- 수입/재정 안정은 이직한다 쪽이 더 유리하다.
- 관계/사회적 연결은 현재 회사에 남는다 쪽이 더 유리하다.

## 5. 차원별 점수표
| 옵션 | 브랜치 | 총점 | emotion | finance | growth | relationships | health | autonomy | regret | risk | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | optimistic | 77 | 55 | 100 | 100 | 55 | 55 | 100 | 43 | 29 | medium |
| A | base | 72 | 55 | 96 | 93 | 55 | 55 | 80 | 43 | 29 | medium |
| A | pessimistic | 33 | 55 | 32 | 0 | 55 | 55 | 16 | 43 | 89 | low |
| B | optimistic | 76 | 100 | 100 | 65 | 100 | 55 | 64 | 43 | 41 | medium |
| B | base | 61 | 43 | 40 | 73 | 100 | 55 | 68 | 43 | 41 | low |
| B | pessimistic | 43 | 25 | 6 | 61 | 27 | 55 | 64 | 43 | 41 | low |

## 6. 주요 분기점
### A / optimistic
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 2: 공통 환경 변화가 finance에 영향을 주었다.

### A / base
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 2: 공통 환경 변화가 finance에 영향을 주었다.

### A / pessimistic
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 1: 예상 밖의 사건이 finance에 부담를 만들었다.

### B / optimistic
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 1: 예상 밖의 사건이 relationships에 호재를 만들었다.

### B / base
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 1: 예상 밖의 사건이 relationships에 호재를 만들었다.

### B / pessimistic
- Turn 1: 공통 환경 변화가 growth에 영향을 주었다.
- Turn 1: 현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.
- Turn 2: 공통 환경 변화가 finance에 영향을 주었다.

## 7. 리스크와 안전장치
- 이 결과는 제공된 입력과 기본 가정에 기반한 시뮬레이션이다. 실제 결과는 외부 변수와 실행 품질에 따라 달라질 수 있다.

## 8. 즉시 구현할 첫 번째 작업 10개
| ID | Priority | Title | Owner | Definition of Done |
| --- | --- | --- | --- | --- |
| P0-1 | P0 | A/B 입력 폼과 기본값 주입 | Frontend | 필수 입력만으로 실행 가능 |
| P0-2 | P0 | Baseline fairness 엔진 | AI | A/B 공통 baseline과 공통 노이즈 보장 |
| P0-3 | P0 | 3-branch 시뮬레이션 생성 | AI | 옵션별 optimistic/base/pessimistic 생성 |
| P0-4 | P0 | 점수/리스크/후회 계산기 | AI | 차원별 점수와 overall score 산출 |
| P0-5 | P0 | 결과 비교 화면 | Frontend | topline verdict와 표/타임라인 렌더링 |
| P0-6 | P1 | 로컬 저장 및 재실행 | Frontend | 최근 실행 결과 로컬 저장 |
| P0-7 | P1 | JSON appendix 다운로드 | Frontend | manifest/scorecard/graph/backlog export 가능 |
| P0-8 | P1 | 민감 도메인 가드레일 적용 | AI | 제한 문구와 비결정성 고지 포함 |
| P0-9 | P1 | 자동 테스트 불변식 | Backend | 정규화, 공정성, 점수 범위 테스트 통과 |
| P0-10 | P2 | PDF-ready export 가이드 | PM | 머지 문서 순서와 포맷 가이드 제공 |

## 9. 머신 리더블 JSON 부록
### simulation_manifest

```json
{
  "decision_title": "이직 vs 현재 회사 잔류",
  "baseline_assumptions": [
    "user_profile이 없어 기본 프로필을 적용했다."
  ],
  "time_horizon": "1_year",
  "mode": "standard",
  "branches_per_option": 3,
  "turns": 12
}
```

### dimension_scorecard

```json
[
  {
    "option": "A",
    "branch": "optimistic",
    "scores": {
      "emotion": 55,
      "finance": 100,
      "growth": 100,
      "relationships": 55,
      "health": 55,
      "autonomy": 100,
      "regret": 43,
      "risk": 29
    },
    "overall_score": 77,
    "confidence": "medium"
  },
  {
    "option": "A",
    "branch": "base",
    "scores": {
      "emotion": 55,
      "finance": 96,
      "growth": 93,
      "relationships": 55,
      "health": 55,
      "autonomy": 80,
      "regret": 43,
      "risk": 29
    },
    "overall_score": 72,
    "confidence": "medium"
  },
  {
    "option": "A",
    "branch": "pessimistic",
    "scores": {
      "emotion": 55,
      "finance": 32,
      "growth": 0,
      "relationships": 55,
      "health": 55,
      "autonomy": 16,
      "regret": 43,
      "risk": 89
    },
    "overall_score": 33,
    "confidence": "low"
  },
  {
    "option": "B",
    "branch": "optimistic",
    "scores": {
      "emotion": 100,
      "finance": 100,
      "growth": 65,
      "relationships": 100,
      "health": 55,
      "autonomy": 64,
      "regret": 43,
      "risk": 41
    },
    "overall_score": 76,
    "confidence": "medium"
  },
  {
    "option": "B",
    "branch": "base",
    "scores": {
      "emotion": 43,
      "finance": 40,
      "growth": 73,
      "relationships": 100,
      "health": 55,
      "autonomy": 68,
      "regret": 43,
      "risk": 41
    },
    "overall_score": 61,
    "confidence": "low"
  },
  {
    "option": "B",
    "branch": "pessimistic",
    "scores": {
      "emotion": 25,
      "finance": 6,
      "growth": 61,
      "relationships": 27,
      "health": 55,
      "autonomy": 64,
      "regret": 43,
      "risk": 41
    },
    "overall_score": 43,
    "confidence": "low"
  }
]
```

### scenario_graph_summary

```json
[
  {
    "option": "A",
    "branch": "optimistic",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 2,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 7,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      }
    ]
  },
  {
    "option": "A",
    "branch": "base",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 4,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 5,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 호재를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      }
    ]
  },
  {
    "option": "A",
    "branch": "pessimistic",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 1,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 부담를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 부담를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 5,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 finance에 부담를 만들었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "이직한다 선택이 growth, autonomy에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "growth",
          "autonomy"
        ]
      }
    ]
  },
  {
    "option": "B",
    "branch": "optimistic",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 1,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 2,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 4,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 5,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 7,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 9,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 11,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      }
    ]
  },
  {
    "option": "B",
    "branch": "base",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 1,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 2,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 3,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 5,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 8,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 10,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 호재를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      }
    ]
  },
  {
    "option": "B",
    "branch": "pessimistic",
    "nodes": [
      {
        "turn": 1,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 1,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 2,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 2,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 3,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 3,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 4,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 4,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 4,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 부담를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 5,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 5,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 6,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 6,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 6,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 부담를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 7,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 7,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 8,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 8,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 8,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 부담를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      },
      {
        "turn": 9,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 9,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 10,
        "event_type": "environment",
        "summary": "공통 환경 변화가 growth에 영향을 주었다.",
        "affected_dimensions": [
          "growth"
        ]
      },
      {
        "turn": 10,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 11,
        "event_type": "environment",
        "summary": "공통 환경 변화가 finance에 영향을 주었다.",
        "affected_dimensions": [
          "finance"
        ]
      },
      {
        "turn": 11,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 12,
        "event_type": "environment",
        "summary": "공통 환경 변화가 autonomy에 영향을 주었다.",
        "affected_dimensions": [
          "autonomy"
        ]
      },
      {
        "turn": 12,
        "event_type": "strategy",
        "summary": "현재 회사에 남는다 선택이 finance, emotion에 직접적인 변화를 만들었다. 특히 재정 안정, 성장 속도 축에서 체감 차이가 커진다.",
        "affected_dimensions": [
          "finance",
          "emotion"
        ]
      },
      {
        "turn": 12,
        "event_type": "chance",
        "summary": "예상 밖의 사건이 relationships에 부담를 만들었다.",
        "affected_dimensions": [
          "relationships"
        ]
      }
    ]
  }
]
```

### mvp_backlog

```json
[
  {
    "id": "P0-1",
    "priority": "P0",
    "title": "A/B 입력 폼과 기본값 주입",
    "owner_hint": "Frontend",
    "definition_of_done": "필수 입력만으로 실행 가능"
  },
  {
    "id": "P0-2",
    "priority": "P0",
    "title": "Baseline fairness 엔진",
    "owner_hint": "AI",
    "definition_of_done": "A/B 공통 baseline과 공통 노이즈 보장"
  },
  {
    "id": "P0-3",
    "priority": "P0",
    "title": "3-branch 시뮬레이션 생성",
    "owner_hint": "AI",
    "definition_of_done": "옵션별 optimistic/base/pessimistic 생성"
  },
  {
    "id": "P0-4",
    "priority": "P0",
    "title": "점수/리스크/후회 계산기",
    "owner_hint": "AI",
    "definition_of_done": "차원별 점수와 overall score 산출"
  },
  {
    "id": "P0-5",
    "priority": "P0",
    "title": "결과 비교 화면",
    "owner_hint": "Frontend",
    "definition_of_done": "topline verdict와 표/타임라인 렌더링"
  },
  {
    "id": "P0-6",
    "priority": "P1",
    "title": "로컬 저장 및 재실행",
    "owner_hint": "Frontend",
    "definition_of_done": "최근 실행 결과 로컬 저장"
  },
  {
    "id": "P0-7",
    "priority": "P1",
    "title": "JSON appendix 다운로드",
    "owner_hint": "Frontend",
    "definition_of_done": "manifest/scorecard/graph/backlog export 가능"
  },
  {
    "id": "P0-8",
    "priority": "P1",
    "title": "민감 도메인 가드레일 적용",
    "owner_hint": "AI",
    "definition_of_done": "제한 문구와 비결정성 고지 포함"
  },
  {
    "id": "P0-9",
    "priority": "P1",
    "title": "자동 테스트 불변식",
    "owner_hint": "Backend",
    "definition_of_done": "정규화, 공정성, 점수 범위 테스트 통과"
  },
  {
    "id": "P0-10",
    "priority": "P2",
    "title": "PDF-ready export 가이드",
    "owner_hint": "PM",
    "definition_of_done": "머지 문서 순서와 포맷 가이드 제공"
  }
]
```