# Report Generator Harness

업무 보고서의 데이터수집→분석→시각화→집필→요약을 에이전트 팀이 협업하여 생성하는 하네스.
출처: [revfactory/harness-100 · ko/82-report-generator](https://github.com/revfactory/harness-100/tree/main/ko/82-report-generator)
(이 저장소는 Daily Papers 아카이브 사이트이며, 이 하네스는 보고서 작성용으로 추가 설치된 것이다.
사이트 빌드 방법은 저장소 루트 `README.md`를 참고한다.)

## 구조

```
.claude/
├── agents/
│   ├── data-collector.md      — 데이터 수집 (소스 탐색, 수치 추출, 정제)
│   ├── analyst.md             — 데이터 분석 (통계, 트렌드, 인사이트 도출)
│   ├── visualizer.md          — 시각화 설계 (차트, 테이블, 인포그래픽 명세)
│   ├── report-writer.md       — 보고서 집필 (구조화된 보고서 작성)
│   └── executive-summarizer.md — 요약 및 교차 검증 (핵심 요약, 정합성 확인)
├── skills/
│   ├── report-generator/
│   │   └── SKILL.md           — 오케스트레이터 (팀 조율, 워크플로우, 에러핸들링)
│   ├── data-visualization-guide/
│   │   └── SKILL.md           — 데이터 시각화 가이드 (visualizer 확장)
│   └── kpi-dashboard-patterns/
│       └── SKILL.md           — KPI 대시보드 설계 패턴 (analyst 확장)
└── CLAUDE.md                  — 이 파일
```

## 사용법

`/report-generator` 스킬을 트리거하거나, "업무 보고서 만들어줘" 같은 자연어로 요청한다.

## 산출물

모든 산출물은 `_workspace/` 디렉토리에 저장된다(`.gitignore` 처리됨):
- `00_input.md` — 사용자 입력 정리
- `01_data_collection.md` — 수집된 데이터 정리
- `02_analysis_report.md` — 분석 결과
- `03_visualization_spec.md` — 시각화 명세
- `04_full_report.md` — 최종 보고서
- `05_executive_summary.md` — 경영진 요약 및 검증 보고
