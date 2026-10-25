import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { BASE_BANK as bank, fingerprint, SUBJECTS, validateQuestion } from "../src/model";

describe("실제 문제은행과 재현성", () => {
  it("120개 실제 등록, 40개씩, 정규화·보기 재배치 중복 없음", () => {
    expect(bank).toHaveLength(120);
    expect(1000 - bank.length).toBe(880);
    expect(new Set(bank.map(q => q.id)).size).toBe(120);
    expect(new Set(bank.map(fingerprint)).size).toBe(120);
    for (const subject of SUBJECTS) expect(bank.filter(q => q.subject === subject)).toHaveLength(40);
    for (const q of bank) {
      expect(() => validateQuestion(q)).not.toThrow();
      expect(q).toMatchObject({year:null, session:null, type:"original", verificationStatus:"reviewed"});
      expect(q.explanation.length).toBeGreaterThan(40);
      expect(q.reviewNote).toContain("외부 전문가 검수 미완료");
      expect(q.rights).toContain("CC BY 4.0");
    }
  });
  it("원고·시드로 재생성 시 은행과 가져오기 양식이 바이트 단위로 같다", () => {
    const files = ["src/data/questions.json", "public/templates/questions.json", "public/templates/questions.csv"];
    const before = files.map(f => readFileSync(f, "utf8"));
    execFileSync("python3", ["scripts/generate_bank.py"]);
    expect(files.map(f => readFileSync(f, "utf8"))).toEqual(before);
  });
  it("개념형 90개, 계산 6유형 × 5조건을 독립 유형과 구별한다", () => {
    expect(bank.filter(q => !q.calculation)).toHaveLength(90);
    expect(bank.filter(q => q.calculation)).toHaveLength(30);
    const families = new Set(bank.filter(q => q.family).map(q => q.family));
    expect(families.size).toBe(6);
    for (const family of families) {
      const questions = bank.filter(q => q.family === family);
      expect(questions).toHaveLength(5);
      expect(new Set(questions.map(q => JSON.stringify(q.calculation?.values))).size).toBe(5);
    }
  });
});

// Separate evaluator from Python generation: explicit physical definitions and
// inverse checks rather than importing generation functions or expected answers.
for (const q of bank.filter(q => q.calculation)) {
  it(`독립 수치·단위·정답·동치 보기 검증 ${q.id}`, () => {
    const {kind, values:v, result, unit} = q.calculation!;
    let computed: number;
    switch(kind) {
      case "amount": computed = v[0] / v[1]; expect(unit).toBe("mol"); break;
      case "molarity": computed = v[0] * 1000 / v[1]; expect(unit).toBe("mol/L"); break;
      case "heat": computed = v[2] * v[1] * v[0]; expect(unit).toBe("J"); break;
      case "mixture": computed = v[1] / 100 * v[0]; expect(unit).toBe("L"); break;
      case "fraction": computed = v[1] / 100 * v[0]; expect(unit).toBe("kg"); break;
      case "leak": computed = v[1] * v[0]; expect(unit).toBe("L"); break;
      default: throw new Error(`未知 formula ${kind}`);
    }
    expect(computed).toBeCloseTo(result, 10);
    const options = q.choices.map(option => {
      const match = option.match(/^([0-9.]+) (.+)$/)!;
      expect(match).not.toBeNull();
      expect(match[2]).toBe(unit);
      return Number(match[1]);
    });
    expect(options[q.answer - 1]).toBeCloseTo(computed, 10);
    expect(options.filter(n => Math.abs(n - computed) < 1e-8)).toHaveLength(1);
    expect(q.explanation).toContain("조건:");
  });
}
