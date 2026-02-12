# PR Reviewer

AI 기반 GitHub Pull Request 자동 코드 리뷰 도구. Cursor IDE와 Claude Code를 모두 지원합니다.

## 사전 준비

- [GitHub CLI (`gh`)](https://cli.github.com/) - 설치 후 `gh auth login` 인증
- [Python 3.x](https://www.python.org/)
- [jq](https://jqlang.github.io/jq/) - JSON 파싱
- [curl](https://curl.se/)
- GitHub Personal Access Token (`repo` 권한)

## 설치

1. `pr-review-tools/.env` 파일 생성 (`.env.example` 참고)

```bash
GITHUB_TOKEN=your_github_token_here
PROJECT_ROOT=/path/to/your/project
```

2. AI 룰 설정
   - **Cursor**: `.cursor/github-pr-review.mdc`가 자동 적용됩니다
   - **Claude Code**: `.claude/commands/review-pr.md`가 자동 적용됩니다

## 사용법

### Cursor

```
123번 PR 리뷰해줘
```

### Claude Code

```
/review-pr 123
```

AI가 자동으로 PR diff를 가져오고, 코드를 분석하고, GitHub에 리뷰 코멘트를 게시합니다.

## 프로젝트 구조

```
pr-reviewer/
├── .claude/commands/
│   └── review-pr.md              # Claude Code 리뷰 커맨드
├── .cursor/
│   └── github-pr-review.mdc      # Cursor AI 리뷰 룰
├── pr-review-tools/
│   ├── fetch_pr_diff.py           # PR diff 가져오기
│   ├── gh-pr-comment.sh           # 라인별 코멘트 게시
│   ├── gh-pr-general-comment.sh   # 일반 코멘트 게시
│   ├── .env                       # 환경 변수 (gitignore)
│   └── .env.example
└── README.md
```
