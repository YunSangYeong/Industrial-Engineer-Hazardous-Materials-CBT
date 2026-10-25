"""Deterministic authored bank; no scraped/past examination content.

Concept manuscripts are reviewed internally for a single correct answer and
scope. Formula tests use a separate JS implementation. Neither is expert review
or a comparison with the official current syllabus.
"""
import csv
import json
import random
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/YunSangYeong/Industrial-Engineer-Hazardous-Materials-CBT/blob/feat/hazardous-materials-cbt/docs/question-review.md"
SUBJECTS = ["일반화학", "화재예방과 소화방법", "위험물의 성질과 취급"]
rng = random.Random(2121001)
bank = []


def add(subject, topic, text, correct, wrong, explanation, **extra):
    index = 1 + sum(q["subject"] == subject for q in bank)
    choices = [correct, *wrong]
    assert len(set(choices)) == 4
    rng.shuffle(choices)
    bank.append(dict(
        id=f"HM-{SUBJECTS.index(subject)+1}-{index:03}",
        subject=subject, topic=topic, question=text, choices=choices,
        answer=choices.index(correct)+1, explanation=explanation,
        difficulty="하", year=None, session=None, type="original",
        sourceUrl=SOURCE, verificationStatus="reviewed",
        reviewNote="AI 일반 지식 기반 자체 작성. 정답 단일성·해설 논리 내부 검토. 공식 자료 대조·외부 전문가 검수 미완료. 작성 기록 URL은 외부 정답 증빙이 아님.",
        version="hazmat-main", rights="자체 제작 · CC BY 4.0 · hazardous-materials-cbt contributors · 기출 아님",
        **extra,
    ))


for row in csv.reader((ROOT / "scripts/concepts.tsv").open(), delimiter="|"):
    assert len(row) == 8, row
    subject, topic, text, correct, *rest = row
    add(subject, topic, text, correct, rest[:3], rest[3])

assert len(bank) == 90


def number(value):
    return format(Decimal(str(value)).normalize(), "f")


def numeric(subject, topic, family, i, text, values, result, unit, explanation):
    result = Decimal(str(result))
    options = [f"{number(result * m)} {unit}" for m in [Decimal("0.5"), Decimal("1.5"), Decimal("2")]]
    add(subject, topic, text, f"{number(result)} {unit}", options, explanation,
        family=family, calculation=dict(kind=family, values=values,
        result=float(result), unit=unit, precision=3))


for i in range(1, 6):
    mass, molar_mass = 18*i, 18
    numeric(SUBJECTS[0], "질량과 물질량", "amount", i,
        f"몰질량이 18 g/mol인 물질 {mass} g의 물질량은?", [mass, molar_mass], i, "mol",
        f"조건: 질량 {mass} g, 몰질량 18 g/mol. 물질량 n=m/M이므로 {mass}/18={i} mol이다. 질량과 몰질량의 g가 약분되어 단위는 mol이며 몰질량은 문제에서 주어진 값이다.")
    moles = Decimal(i)/10
    concentration = moles/Decimal("0.5")
    numeric(SUBJECTS[0], "몰 농도 계산", "molarity", i,
        f"용질 {number(moles)} mol을 녹여 최종 용액 부피를 500 mL로 만들었다. 몰 농도는?", [float(moles), 500], concentration, "mol/L",
        f"조건: 용질 {number(moles)} mol, 최종 용액 500 mL. 500 mL=0.5 L이므로 C=n/V={number(moles)}/0.5={number(concentration)} mol/L이다. 용매 부피가 아닌 최종 용액 부피를 사용한다.")
    mass = 100*i
    heat = Decimal(mass)*Decimal("4.2")*10
    numeric(SUBJECTS[1], "냉각 열량", "heat", i,
        f"물 {mass} g의 온도를 10 K 올리는 데 필요한 열량은? 비열은 4.2 J/(g·K), 열손실과 상태 변화는 무시한다.", [mass, 4.2, 10], heat, "J",
        f"조건: 물 {mass} g, 비열 4.2 J/(g·K), 온도 차 10 K. Q=mcΔT={mass}×4.2×10={number(heat)} J이다. g와 K가 약분된다. 상태 변화가 없으므로 기화열은 더하지 않는다.")
    volume = 100*i
    concentrate = Decimal(volume)*Decimal("0.03")
    numeric(SUBJECTS[1], "소화 혼합액 산술", "mixture", i,
        f"부피 기준 농도 3%인 모의 소화 혼합액 {volume} L를 계산상 만들 때 원액 부피는? 부피 가산성을 가정하며 특정 제품의 실제 혼합 지침은 아니다.", [volume, 3], concentrate, "L",
        f"조건: 최종 혼합액 {volume} L, 부피 분율 3%=0.03. 원액 V={volume}×0.03={number(concentrate)} L이다. 최종 부피를 기준으로 한다. 산술 학습 문제이며 제품별 실제 사용 농도·적합성은 별도 확인한다.")
    total = 20*i
    solute = Decimal(total)*Decimal("0.25")
    numeric(SUBJECTS[2], "혼합물 함량", "fraction", i,
        f"질량 기준 함량 25%인 위험물 모의 시료 {total} kg에 포함된 해당 성분의 질량은? 특정 법령의 판정 문제는 아니다.", [total, 25], solute, "kg",
        f"조건: 시료 전체 {total} kg, 성분 질량 분율 25%=0.25. 성분 질량={total}×0.25={number(solute)} kg이다. 순도에 따른 법령 적용이나 지정수량을 계산하는 문제는 아니다.")
    rate, minutes = 2*i, 5
    leaked = rate*minutes
    numeric(SUBJECTS[2], "누출 부피 추정", "leak", i,
        f"모의 누출량 산술에서 일정 체적 유량 {rate} L/min이 {minutes}분간 지속되었다. 증발·회수·반응을 무시한 누출 부피는?", [rate, minutes], leaked, "L",
        f"조건: 일정 체적 유량 {rate} L/min, 지속 시간 {minutes} min. V=유량×시간={rate}×{minutes}={leaked} L이다. min이 약분된다. 실제 현장 확산이나 안전거리 산정 결과를 뜻하지 않는다.")

bank.sort(key=lambda q: q["id"])
assert len(bank) == 120
assert all(sum(q['subject'] == s for q in bank) == 40 for s in SUBJECTS)
(ROOT / "src/data/questions.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2)+"\n")

# Import templates remain pending and have a distinct ID and stem.
template = dict(bank[0], id="LOCAL-TEMPLATE-001", question="양성자 수가 같은 원자들을 같은 원소로 분류하는 기준은?",
    choices=["원자 번호", "용기 색", "보관 위치", "물질의 가격"], answer=1,
    explanation="원자 번호는 양성자 수이며 같은 원소의 기본 분류 기준이다. 사용자가 출처·이용 조건·정답을 확인한 후 로컬 검수를 승인해야 한다.",
    verificationStatus="pending", reviewNote="사용자 검수 전에는 학습에 사용하지 않는 자체 제작 예시")
templates = ROOT / "public/templates"
templates.mkdir(parents=True, exist_ok=True)
(templates / "questions.json").write_text(json.dumps([template], ensure_ascii=False, indent=2)+"\n")
csv_template = {k:v for k,v in template.items() if k != 'choices'}
csv_template.update({f"choice{i+1}": v for i,v in enumerate(template['choices'])})
with (templates / 'questions.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=csv_template.keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerow({k: '' if v is None else v for k,v in csv_template.items()})
print("120 authored questions: 90 concepts + 6 numeric families × 5 conditions; 40 per subject")
