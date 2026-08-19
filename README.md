# Daily Papers 아카이브

[huggingface.co/papers](https://huggingface.co/papers)의 일별 업보트 상위 논문을 한글로 분석해 정리하는 정적 아카이브 사이트입니다. 날짜별로 조회하거나 키워드로 검색할 수 있습니다.

GitHub Pages로 배포되며, `index.html`이 진입점입니다.

## 폴더 구조

```
index.html          날짜 선택 + 키워드 검색 + 카테고리 필터가 있는 메인 페이지
data/
  index.json         존재하는 날짜 목록
  YYYY-MM-DD.json    해당 날짜의 논문 목록(제목/한글제목/요약/링크 등) — build_site.py 생성 결과
  day_config/
    YYYY-MM-DD.json  해당 날짜 논문의 원본 메타데이터(rank/카테고리/upvote/원제목/한글제목/베이스파일명) — 사람 또는 자동화가 직접 작성
papers/
  <arXiv ID>_new.html  논문별 상세 분석 페이지
scripts/
  build_site.py        summary 마크다운 + data/day_config/*.json -> data/*.json + papers/*.html 생성 스크립트
```

## 새 날짜 추가하는 방법

1. `paper-analyzer` 에이전트(`.claude/agents/paper-analyzer_new.md`)로 그날의 논문들을 분석해 `downloads/{베이스파일명}_summary_new.md`를 생성합니다.
2. `data/day_config/{날짜}.json` 파일을 새로 작성합니다 (arXiv ID별 rank/카테고리/upvote/원제목/한글제목/베이스파일명). **파이썬 소스(`build_site.py`)는 건드리지 않습니다** — 데이터 파일만 추가하면 됩니다.
3. 스크립트를 실행합니다.

   ```bash
   py -3 scripts/build_site.py
   ```

4. `data/{날짜}.json`, `data/index.json`, `papers/*.html`이 갱신됩니다. 변경 사항을 커밋하고 푸시하면 GitHub Pages에 반영됩니다.

## 참고

- `downloads/`(원문 PDF, 추출 텍스트)는 저작권 문제로 이 저장소에 포함하지 않습니다(`.gitignore` 처리). 각 논문 상세 페이지에는 arXiv 원문으로 연결되는 링크만 제공합니다.
- 모든 요약·번역은 원문을 재구성한 것이며, 원문을 그대로 옮기지 않습니다.
