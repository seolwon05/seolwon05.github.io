# 새 글 올리기

이 블로그의 글은 Jekyll이 `_posts` 폴더의 Markdown(`.md`) 파일을 읽어 만듭니다. GitHub 웹사이트에서 파일을 새로 만들거나 완성한 `.md` 파일을 업로드해도 됩니다. `main` 브랜치에 저장하면 GitHub Pages 배포 작업이 자동으로 실행됩니다.

1. [`_drafts/post-template.md`](_drafts/post-template.md)의 내용을 복사합니다.
2. GitHub 저장소의 `_posts` 폴더에서 **Add file → Create new file**을 누릅니다. 이미 작성한 파일이 있다면 **Upload files**를 선택합니다.
3. 파일 이름을 `YYYY-MM-DD-english-slug.md` 형식으로 정합니다. 예: `2026-11-12-my-first-project.md`. 날짜는 본문의 `date`와 같게 입력하고, 영어 slug는 다른 글과 겹치지 않게 합니다. 이 예시의 글 주소는 `/posts/my-first-project/`입니다.
4. `title`, `date`, `description`, `categories`, `tags`와 본문을 실제 내용으로 바꿉니다. `date`는 `2026-11-12 12:00:00 +0900`처럼 한국 시간대를 포함합니다. 미래 시각으로 적으면 게시 전까지 보이지 않을 수 있습니다.
5. **Commit changes**를 눌러 `main` 브랜치에 저장합니다. 배포가 끝나면 블로그의 홈, 해당 카테고리, 태그, 아카이브에서 글을 확인합니다.

## 카테고리와 태그

사건 보드의 기존 분류를 사용하려면 `categories`에는 아래 이름 중 하나를 **정확히** 적습니다. 철자나 공백이 다르면 다른 분류로 처리됩니다.

| 카테고리 | 기존 태그 예시 |
| --- | --- |
| `Development` | `programming` |
| `CTF & Wargame` | `ctf` |
| `Bug Bounty` | `bug-bounty` |
| `Tech Notes` | `notes` |
| `Research & Conference` | `research` |
| `Activities & Certifications` | `activities` |

태그는 여러 개를 적을 수 있습니다. 예: `tags: [programming, notes]`. 새 태그를 쓰면 태그 목록에 새 티켓이 생깁니다.

`description`은 선택 사항입니다. 글 상세의 보고서 제목 아래에 표시됩니다. `layout`은 적지 않아도 기본값인 `case-report`가 적용됩니다. 본문의 첫 번째 `# 제목`은 기존 글과 같은 형식이며, 파일 맨 위의 `title`이 보고서 제목으로 표시됩니다.
