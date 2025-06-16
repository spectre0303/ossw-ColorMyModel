# 🎨 ColorMyModel - 프라모델 채색 가이드 앱

**팀명: GDB**  
**프로젝트명: ColorMyModel**
<p align="center">
  <img src="https://github.com/spectre0303/ossw-ColorMyModel/blob/main/ColorMyModel_Logo.png?raw=true" alt="ColorMyModel Logo" width="250"/>
</p>

<p align="center">🖌️ 흑백 도안을 자동 채색하는 프라모델 도색 가이드 앱</p>

프라모델 흑백 도안을 업로드하면,  
👉 색상 코드 추출 → 👉 윤곽선/명암 기반 영역 분리 → 👉 자동 채색 → 👉 결과 이미지 출력까지!  
초보자도 쉽게 따라할 수 있는 **프라모델 자동 채색 가이드 앱**입니다.
## 🔍 프로젝트 소개

### 🙋 왜 이 프로젝트를 시작했나요?

프라모델(플라스틱 모델 키트) 도색 설명서는 대부분 **흑백 도안**으로 제공되며, 초보자는 영역 구분이나 색상 매칭에 어려움을 겪습니다.  
우리는 "초보자도 쉽게 접근 가능한 자동 채색 가이드가 있다면 좋겠다"는 아이디어에서 이 프로젝트를 시작하게 되었습니다.

---

### 🧩 어떤 문제를 해결할 수 있나요?

- 흑백 도안에서 **색상 코드**를 자동으로 추출하고  
- 윤곽선과 명암 기반으로 **채색 영역을 자동 분할**하고  
- 인식된 코드에 따라 **자동 채색 시뮬레이션**을 제공합니다.  

이를 통해 사용자는 실제 도색 전에 **완성된 결과를 미리 시각화**할 수 있으며, 실수를 줄이고 도색에 자신감을 가질 수 있습니다.

---

### 📚 프로젝트를 통해 무엇을 배웠나요?

- **OCR 튜닝 및 이미지 전처리** 기술의 복잡성  
- **색상 정보 파싱 및 매핑**의 실제 어려움 (코드 조합, 유사 이름 등)  
- Flutter를 활용한 **간단한 반응형 UI 구성 방식**  
- 팀원 간 협업 및 버전 관리(GitHub / Notion)의 중요성  
- 기능별 모듈화를 통한 **재사용 가능한 코드 작성 경험**

---

### 🌟 이 프로젝트의 장점은 무엇인가요?

- ✅ 초보자도 쉽게 사용할 수 있는 직관적인 UI  
- ✅ 다양한 언어(일본어, 영어, 중국어)의 색상 코드 인식 지원  
- ✅ 흐릿하거나 어두운 이미지도 자동 필터링하는 **품질 검사 기능**  
- ✅ 수동/자동 채색 모드 지원 (랜덤 색상 + 수동 선택 기능)  

---

## 👥 팀 구성원 및 역할

| 이름       | 역할           |
|------------|----------------|
| 진민규, 전지민 | 앱 개발 (Flutter) |
| 성연지, 홍철민 | 주요 기능 개발    |
| 바담수렌     | 프로젝트 문서화   |

---

## 💻 기술 스택

### 🛠️ 백엔드

| 구분 | 라이브러리 | 설명 |
|------|------------|------|
|이미지 처리 & 색칠 | [<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white">](https://opencv.org) [<img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white">](https://numpy.org) [<img src="https://img.shields.io/badge/Pillow-cc0066?style=for-the-badge&logo=python&logoColor=white">](https://python-pillow.org) [<img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white">](https://scikit-learn.org/stable/modules/clustering.html) [<img src="https://img.shields.io/badge/colorsys-FFD700?style=for-the-badge&logo=python&logoColor=white">](https://docs.python.org/3/library/colorsys.html) [<img src="https://img.shields.io/badge/random-777777?style=for-the-badge&logo=python&logoColor=white">](https://docs.python.org/3/library/random.html) | 도안 채색 영역 분할 및 자동 색상 부여 |
| 텍스트 인식 | [<img src="https://img.shields.io/badge/easyOCR-FFD43B?style=for-the-badge&logo=python&logoColor=black">](https://github.com/JaidedAI/EasyOCR) | 다양한 언어 인식, 정규식 + 전처리로 색상 코드 정확도 향상 |
| 번역 | [<img src="https://img.shields.io/badge/googletrans-34A853?style=for-the-badge&logo=google&logoColor=white">](https://py-googletrans.readthedocs.io/en/latest/) | 다국어 색상명 자동 번역 처리 |

---

### 🎨 프론트엔드

| 구분 | 라이브러리 | 설명 |
|------|------------|------|
| 앱 구현 | [<img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white">](https://flutter.dev) | iOS 및 Android 모두 지원하는 앱 개발 |

---

### 🤝 협업 도구

| 도구 | 설명 |
|------|------|
| [<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">](https://github.com) | 소스 코드 버전 관리 |
| [<img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white">](https://www.notion.so/) | 팀 문서 및 진행 관리 |


---

## 🎯 MVP 목표

- 흑백 도안에서 **색상 코드 자동 인식**
- **윤곽선 + 명암 기반 자동 영역 분리**
- 영역별로 알맞은 색상 자동 채색
- 최종 결과를 **PNG 이미지로 출력**
- 초보자도 사용할 수 있도록 **언어 및 형식 통합 제공**

---

## 🛠️ 핵심 기능

✅ 도안 이미지 업로드 및 인식 확인  
✅ 윤곽선 + 명암 기반 구역 분리  
✅ 색상 코드 OCR 추출 (일본어, 중국어, 영어)  
✅ 화살표 및 도형 영역 추적  
✅ 색상 매핑 및 자동 채색  
✅ 채색된 도안 이미지 PNG로 출력

---

## 🚫 MVP에서 제외한 기능

- 전체 설명서 채색 적용
- 도료 회사별 대체 색상 정보 제공
- 사용자 지정 색상 매핑

---

## 📏 완성 목표 (측정 기준)

| 기능 항목                          | 비율 |
|-----------------------------------|------|
| 흑백 도안 업로드 성공              | 15% |
| 색상 코드 인식 (OCR)              | 20% |
| 윤곽선 + 명암 기반 영역 분리       | 30% |
| 색상 매핑 및 자동 채색            | 25% |
| PNG 결과 이미지 출력              | 10% |
| **총합**                          | **100%** |

**성공 기준:**
- 색상 번호 인식률
- 영역 분리 정확도
- 최종 이미지 출력 성공 여부

---

## 📌 향후 확장 가능성

- 전체 도안 자동 채색
- 사용자 맞춤 색상 설정
- AI 기반 색상 추천
- 도료 브랜드 간 호환 색상 추천 시스템
  
##  💻 프로젝트 설치 방법


본 프로젝트는 **백엔드 서버**와 **Flutter 웹 클라이언트**로 구성되어 있으며, 두 구성 요소 모두 실행되어야 전체 기능을 사용할 수 있습니다.

---

### 🖥️ 1. 서버 실행 방법 (Python)

#### ✅ 저장소 클론
```bash
git clone https://github.com/spectre0303/ossw-ColorMyModel.git
cd ossw-ColorMyModel
```

#### ✅ (선택) 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows는 venv\Scripts\activate
```

#### ✅ 패키지 설치
```bash
pip install -r requirements.txt
```

#### ✅ 백엔드 서버 실행
```bash
python main.py
```

---

### 🌐 2. 클라이언트 실행 방법 (Flutter Web)

#### ✅ Flutter SDK 설치
Flutter 설치 여부 확인:
```bash
flutter --version
```
설치되지 않았다면 [Flutter 설치 가이드](https://docs.flutter.dev/get-started/install)를 참고하세요.

#### ✅ 프로젝트 디렉토리로 이동
압축을 풀었거나 복사한 Flutter 프로젝트 폴더로 이동합니다.

#### ✅ 의존성 설치
```bash
flutter pub get
```

#### ✅ main.dart 파일 위치 확인
`lib/main.dart`가 있는지 확인합니다.

#### ✅ 에뮬레이터 또는 디바이스 준비
Chrome 브라우저를 기본 디바이스로 실행하거나, Android Studio/VS Code에서 실행할 수 있습니다.
```bash
flutter run -d chrome
```

> ⚠️ **중요:** 서버가 반드시 백그라운드에서 구동 중이어야 하며,  
> `main.dart`의 `Uri.parse`에 지정된 주소는 서버와 동일한 IP로 수정해야 합니다.


---

## 📱 프로젝트 사용법

### 앱 사용 흐름

1. 프라모델 도안 이미지 업로드
2. 품질 체크 (흐림/어두움 등 자동 판별)
3. OCR로 색상 코드 자동 인식
4. 윤곽선+명암 기반 영역 분리
5. 자동 채색 또는 수동 색상 선택
6. 결과 이미지 다운로드

> 📌 **추가 정보**  
> - 수동 채색 시, 색상 스포이트 도구로 영역 클릭 가능  
> - Ver1/Ver2 분할 방식 중 선택 가능  
> - 출력 파일은 `/output/` 경로에 저장
  
## 📚 회의록 모음 및 진행 상황

프로젝트의 주간 회의록 및 기능별 개발 진행 상황은 GitHub Wiki에 정리되어 있습니다.  
👉 [회의록 모음 및 진행 상황 바로가기](https://github.com/spectre0303/ossw-ColorMyModel/wiki)


## ✅ 팀원별 진행 상황 정리

| 팀원     | 완료된 작업 | 현재 문제 | 5월 19일까지 목표 |
|----------|-------------|-----------|-------------------|
| **홍철민**   | - OCR을 활용한 문자/명칭 기반 코드 작성 완료<br>- 색상 추출부 코드 완료<br>- Jupyter Notebook에 상세 설명 포함 | - OCR 결과에서 인식되지 않는 파트가 있음<br>- 복잡한 입력값(Xf-?, T-S-? 등) 처리를 위한 파싱 로직 필요 | - OCR을 위한 입력값 처리 개선<br>- 파트명 자동 매핑 정확도 향상 |
| **성연지**   | - 적정 이미지 검출 구현 완료<br>- 음영 기반 도색 파트 분할 구현 완료 | - OCR 정확도 부족<br>- 파트 구분 및 연결 정확도 낮음 | - 다양한 입력값을 추가로 테스트하여 수정이 필요한 부분을 확인하고, 색상 표기(XF, X, TS, H 등)에 대응하는 실제 RGB 값을 매핑한 색상표를 생성할 예정입니다. |
| **전지민**   | - 이미지 업로드 기능 구현<br>- 파이썬 서버 전송 및 디버깅용 이미지 변환 완료 | - 서버에서 다시 이미지 받아오는 기능 미작동 | - 이미지 재수신 기능 완성 (파이썬 서버 → 프론트) |
| **진민규**   | - 기본 틀 및 대부분 핵심 기능 구현 완료 | - 서버에서 처리된 데이터를 프론트에서 인식하지 못함 | - 데이터 연결 완성<br>- 여유 시 UI/디자인 작업 수행 |
| **바담수렌** | - 팀원 진행 상황 수집 및 문서화<br>- 발표 PPT 기본 틀 초안 구성 시작 | - 발표 흐름과 시각적 구성 방식 정리 필요<br>- 문서와 발표 내용의 연결성 확보 | - PPT 구조 확정 및 초안 완성<br> |

---

## 🔍 기능별 세부 진행 상황

| **기능** | **5/29 상태** | **6/6 상태** |
|---------|---------------|--------------|
| **1. 이미지 품질 판별** | - 업로드 후 별도 품질 검사 없음<br>- 저해상도·흐림·어두운 이미지가 자동으로 걸러지지 않음 | - CV2 Laplacian Variance 사용해 “선명 vs 흐림” 판단 (threshold=100)<br>- mean_intensity 이용해 “어두움<50 / 밝음>200” 판별<br>- gray max-min 대비로 “저명암(<50)” 판별<br>- 해상도 기준(w,h<1000)으로 “저해상도” 자동 감지<br>→ 모든 품질 예외(흐림/어두움/저해상도/저명암) 자동 알림 |
| **2. OCR 튜닝 및 엔진 변경** | - pytesseract 기반 단순 전처리(Grayscale→Binary) 사용<br>- 인식률 약 30% 미만<br>- 색상 코드(숫자+문자) 인식 불안정 | - easyOCR 채택 후 전처리 모듈 강화:<br>  • Upscaling(옵션, cubic interpolation)<br>  • Noise Reduction(h=10~20)<br>  • Grayscale → OTSU Thresholding → Adaptive Thresholding(kernel=3×3, 속도 느림 대신 정밀도↑)<br>  • Morphological Operation(Opening/Closing) 적용<br>- Contour 기반 텍스트 읽기는 폐기<br>- 최종적으로 “Adaptive Thresholding + easyOCR + 정규식(‘XF-\d+’, ‘H\d+’, 숫자+색상이름) + CSV DB 매칭” 방식으로 인식률 크게 향상 |
| **3. 윤곽선 기반 구역 분리** | - Canny + Contour 방식 단일 적용<br>- 전체 윤곽선이 남아 있으면 구역이 과분할되거나 흰 배경이 별도로 분리됨<br>- 외곽 윤곽선 감지 후 불안정하게 구분됨 | - **Ver1 (Aggressive)**: Canny → 불필요한 작은 선 모두 제거 → 외곽 윤곽선만 추출 (글자 심볼 뿐만 아니라 의미 있는 구역의 일부도 함께 소실 문제 발생)<br>- **Ver2 (Conservative)**: 기존 Canny+Contour 방식 유지 → 노이즈 선 포함하지만 필수 구역은 놓치지 않음<br>- 두 버전을 모두 사용하여 이미지 유형에 따라 선택 가능<br>- 전체 윤곽선 중 이미지 면적의 ≥60% 차지하는 윤곽선은 ‘외곽선’으로 판단 후 삭제<br>- 영역 분할 후 랜덤 색상 매칭 모듈:<br>  • Hue 균등 분포 방식으로 시각적 구분도↑<br>  • 채도/명암 범위 한으로 채도가 너무 높거나 낮지 않게 생성<br>  • 중복 색상 배제 |
| **4. 색상 코드 매핑·채색** | - 랜덤 색상만 입혀 보고 수동 매핑 UI 없음 | - **수동 매핑 UI 구현**: 마우스 클릭으로 특정 구역 선택 → 임의 랜덤 색상(또는 스포이트 색) 입힘<br>- “색상 스포이트 툴” 도입: 이미지 내 픽셀 클릭 시 해당 RGB 추출 가능<br>- 랜덤 색상 생성 로직 고도화: Hue 균등 분포, 채도/명암 제한, 색 중복 방지<br>- “실제 색상표 CSV” 연동 준비 중:<br>  • XF, X, TS, H 등 도료 코드 표 → RGB 매핑 함수 설계<br>  • 예: “XF-63:1+XF-53:2” 복합 라벨 파싱 아이디어 구상 |
| **5. 결과 저장·다운로드** | - 채색 결과를 화면에만 표시<br>- 파일 저장/다운로드 기능 없음 | - **PNG/JPEG 저장 기능 구현**: `main.py` 실행 시 3~4초 내에 채색 결과 이미지 생성 가능<br>- UI 내 “다운로드” 버튼 클릭 시 브라우저 기본 다운로드 작동 확인<br>- “저장 폴더 지정” 옵션 미구현(기본 다운로드 폴더에 저장) |
| **6. UI 전체 구성 및 반응형 대응** | - Flutter/Dart 템플릿 채택만 되어 있음<br>- “업로드→OCR→채색→저장” 순서별 메뉴 배치 미완성<br>- 모바일/반응형 지원 전무 | - **데스크톱용 기본 흐름 완성**:<br>  • 좌측 사이드바(업로드, OCR, 분할, 채색, 저장 메뉴) 배치<br>  • 우측 메인 화면에 해당 단계별 UI 렌더링<br>  • “버전 선택(Ver1/Ver2)” 버튼, “Quality Check” 팝업 연동<br>- **Help/FAQ** 안내 문구 구상만 완료(팝업 미구현)<br>- **모바일/반응형** 테스트 미실시 |
| **7. 문서화 및 발표 자료 준비** | - 노션(Notion) 문서 초안 일부 작성, 주요 기능 설명·스크린샷 누락<br>- 슬라이드 초안 작성 중, 구조 정리만 완료 | - **노션 문서화 완료**:<br>  • 기능별 워크플로우(스크린샷·코드 스니펫 포함)<br>  • 예외 케이스(어두움/흐림/명암 문제)<br>  • 전처리 단계별 이미지 예시(Adaptive Threshold, Morphology 등)<br>  • Ver1 vs Ver2 비교 예시 스크린샷<br>  • GitHub PR 링크 첨부<br>- **슬라이드 업데이트 완료**:<br>  • Before/After 스크린샷 반영<br>  • 기능별 설명 보강<br>  • Next Action 부분 추가 |
---

## 📎 참고 링크 및 가이드

### 🐛 Issue & 기능 제안
ColorMyModel에서 발생한 문제나 개선 사항, 새 기능 아이디어가 있다면 언제든지 이슈를 등록해주세요.  
- [Issue 등록하기](https://github.com/spectre0303/ossw-ColorMyModel/issues)
- [기능 제안 템플릿](https://github.com/spectre0303/ossw-ColorMyModel/issues/new?template=feature_request.md)

### 📥 Pull Request
기여하고 싶으신가요? 환영합니다! 아래 절차에 따라 PR을 보내주세요.
1. 저장소 Fork
2. 새로운 브랜치 생성
3. 기능 개발 후 커밋
4. [Pull Request 작성](https://github.com/spectre0303/ossw-ColorMyModel/pulls)

> 📌 PR 전에는 반드시 [CONTRIBUTING.md](./CONTRIBUTING.md) 문서를 읽어주세요.

### 📚 위키 (Wiki)
- ColorMyModel 프로젝트 구조, 기술 설명 등은 [Wiki 페이지](https://github.com/spectre0303/ossw-ColorMyModel/wiki)에서 확인 가능합니다.
- 주요 내용:
  - 프로젝트 소개 및 사용 가이드
  - 이미지 처리 흐름
  - OCR/채색 알고리즘
  - UI 구성 및 전처리 시각 자료


### 🙌 기여 가이드
ColorMyModel은 누구나 기여할 수 있습니다. 자세한 기여 방법은 [CONTRIBUTING.md](./CONTRIBUTING.md)를 참고해주세요.

## 🧾 라이선스

Copyright (c) 2025 GDB Team

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](./LICENSE)를 참고하세요.
