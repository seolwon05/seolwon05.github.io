---
title: "글 제목"
date: 2026-11-23 12:00:00 +0900
description: "글 목록과 사건 보고서 상단에 표시할 한 줄 소개"
# thumbnail: "/assets/img/posts/대표-이미지.jpg"
categories:
  - "Development"
tags: [programming]
---

# 글 제목

글의 핵심 내용을 한두 문장으로 소개합니다.

## 배경

이 기록을 남기게 된 이유와 상황을 적습니다.

## 조사 및 진행 과정

시도한 방법, 참고 자료, 판단 근거를 순서대로 적습니다.

## 결과와 배운 점

결과와 다음에 다시 확인할 내용을 적습니다.

---

## 작성 안내 (새 글에 복사할 때는 이 아래를 지우세요)

새 글은 `_posts/YYYY-MM-DD-영문-파일명.md`로 만듭니다. 맨 위 `---` 사이의 제목, 날짜, 소개, 카테고리, 태그를 글에 맞게 바꾸세요. 이 `_drafts` 파일 자체는 공개 글 목록에 나오지 않습니다.

### 카테고리와 태그

케이스 보드에 준비된 카테고리는 아래 **6개**입니다. `categories`에는 표시된 영문 이름을 그대로 적으세요.

| 카테고리 | 용도 예시 |
|---|---|
| `Development` | 개발 기록 |
| `CTF & Wargame` | CTF·워게임 풀이 |
| `Bug Bounty` | 버그바운티 기록 |
| `Tech Notes` | 기술 문서·학습 기록 |
| `Research & Conference` | 연구·논문·컨퍼런스 |
| `Activities & Certifications` | 활동·자격증 |

태그 페이지는 글의 `tags` 값에서 자동으로 만들어집니다. 지금까지 사용하거나 예시로 정해 둔 태그는 `activities`, `bug-bounty`, `ctf`, `notes`, `programming`, `research`입니다. 새 태그도 만들 수 있으며, 태그가 달린 글이 없으면 태그 목록에 표시되지 않습니다.

```yaml
categories:
  - "CTF & Wargame"
tags: [ctf, notes]
```

### 대표 이미지와 본문 사진

이미지 파일을 `assets/img/posts/`에 올린 뒤 경로를 정확히 적습니다. 대소문자도 파일명과 일치해야 합니다.

```yaml
thumbnail: "/assets/img/posts/my-cover.png"
```

```markdown
![사진 설명](/assets/img/posts/my-photo.png)
```

`thumbnail`은 글 목록의 썸네일입니다. 본문에도 표시하려면 `![사진 설명](...)`을 별도로 넣으세요.

### 코드 블록

시작 표시의 언어명을 `python`, `bash`, `javascript` 등으로 바꾸면 코드 강조가 적용됩니다.

````markdown
```python
from pwn import *
print("hello")
```
````

### 설명 카드(용어 메모)

문장 속에서 설명을 붙일 위치에 아래 include를 넣습니다. PC에서는 커서를 올리고, 키보드나 터치에서는 해당 문구를 선택하면 설명이 보입니다. 실제 예시는 ROP 글의 x86 풀이 중 `Segmentation fault`입니다.

```liquid
{% include annotation.html text="Segmentation fault" note="허용되지 않은 메모리 접근 등으로 프로그램이 종료될 때 나타나는 오류입니다." %}
```

### 콜아웃

`>`는 인용문이므로 설명 카드형 콜아웃은 아래 HTML을 사용합니다. `markdown="1"`을 넣고 제목·본문·닫는 태그 사이에 빈 줄을 둡니다. 콜아웃을 중첩하지 마세요.

```html
<aside class="case-callout" markdown="1">

<p class="case-callout-title">핵심 메모</p>

여기에 설명을 적습니다. **굵은 글씨**도 사용할 수 있습니다.

</aside>
```

콜아웃 안에 표를 넣을 때도 제목과 표 사이, 표와 `</aside>` 사이에 빈 줄을 둡니다.

```html
<aside class="case-callout" markdown="1">

<p class="case-callout-title">예시 입력</p>

| 입력값 | 테스트 목적 |
|---|---|
| `0` | 경계값 확인 |
| `-1` | 음수 처리 확인 |

</aside>
```

### 접었다 펴는 토글

`<summary>`에는 접힌 상태에서도 보일 제목을 적고, 숨길 내용만 `<details>` 안에 둡니다. 밖에 보여야 할 문장은 반드시 `</details>` 다음에 적습니다. 토글 안에서 이미지·표·마크다운을 쓰려면 `markdown="1"`과 빈 줄이 필요합니다.

```html
<details markdown="1">
<summary>자세한 설명</summary>

숨겨 둘 내용입니다.

![추가 사진](/assets/img/posts/my-photo.png)

</details>

이 문장은 토글을 열지 않아도 보입니다.
```

### 일반 표와 구분선

표 **앞뒤에 빈 줄**을 넣으세요. 특히 표 바로 뒤에 `<br>` 같은 HTML 태그를 붙이면 블로그에서는 표 전체가 일반 텍스트로 보일 수 있습니다.

```markdown
표를 소개하는 문장입니다.

| 항목 | 내용 |
|---|---|
| 첫째 | 설명 |
| 둘째 | 설명 |

다음 문장입니다.
```

문단 사이의 구분선은 빈 줄을 두고 `---`를 적습니다.

```markdown
윗문단.

---

아랫문단.
```

새로운 작성 기능을 추가할 때 이 안내에도 사용 예시를 계속 추가합니다.
