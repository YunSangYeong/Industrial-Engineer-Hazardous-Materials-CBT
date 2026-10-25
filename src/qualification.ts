// Official source access was denied. These are explicit learning assumptions,
// not a claim that the current official examination standard was verified.
export const PROFILE = {
  name: "위험물산업기사",
  title: "위험물산업기사 필기 CBT",
  bankId: "hazmat-main",
  subjects: ["일반화학", "화재예방과 소화방법", "위험물의 성질과 취급"] as const,
  questionsPerSubject: 20,
  questionCount: 60,
  durationMinutes: 90,
  choiceCount: 4,
  passScore: 60,
  subjectCutoff: 40,
  maxScore: 100,
  storageKey: "hazardous-materials-cbt:v1",
  rulesVerificationStatus: "pending",
  officialSource: "https://www.q-net.or.kr/crf005.do?id=crf00503&jmCd=2121",
} as const;
