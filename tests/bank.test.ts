import { describe, expect, it } from "vitest";
import { createHash } from "node:crypto";
import summary from "../src/data/bank-summary.json";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { BASE_BANK as bank, fingerprint, SUBJECTS, validateQuestion } from "../src/model";

describe("실제 문제은행과 재현성", () => {
  it("1,000개 실제 등록, 과목별 350/325/325개, 정규화·보기 재배치 중복 없음", () => {
    expect(bank).toHaveLength(1000);
    expect(1000 - bank.length).toBe(0);
    expect(new Set(bank.map(q => q.id)).size).toBe(1000);
    expect(new Set(bank.map(fingerprint)).size).toBe(1000);
    SUBJECTS.forEach((subject, i) => expect(bank.filter(q => q.subject === subject)).toHaveLength([350,325,325][i]));
    for (const q of bank) {
      expect(() => validateQuestion(q)).not.toThrow();
      expect(q).toMatchObject({year:null, session:null, type:"original", verificationStatus:"reviewed"});
      expect(q.explanation.length).toBeGreaterThan(40);
      expect(q.reviewNote).toContain("외부 전문가 검수 미완료");
      expect(q.rights).toContain("CC BY 4.0");
    }
  });
  it("원고·시드로 재생성 시 은행과 가져오기 양식이 바이트 단위로 같다", () => {
    const files = ["src/data/questions.json", "public/templates/questions.json", "public/templates/questions.csv", "src/data/bank-summary.json"];
    const before = files.map(f => readFileSync(f, "utf8"));
    execFileSync("python3", ["scripts/generate_bank.py"]);
    expect(files.map(f => readFileSync(f, "utf8"))).toEqual(before);
  });
  it("개념형 170개, 계산 830개/46개 family의 실제 조건 수를 구별한다", () => {
    expect(bank.filter(q => !q.calculation)).toHaveLength(170);
    expect(bank.filter(q => q.calculation)).toHaveLength(830);
    const families = new Set(bank.filter(q => q.family).map(q => q.family));
    expect(families.size).toBe(46);
    for (const family of families) {
      const questions = bank.filter(q => q.family === family);
      const originalFamilies = ["amount", "molarity", "heat", "mixture", "fraction", "leak"];
      const count = originalFamilies.includes(family!) ? 5 : 20;
      expect(questions).toHaveLength(count);
      expect(new Set(questions.map(q => JSON.stringify(q.calculation?.values))).size).toBe(count);
    }
  });
  it("기존 120개의 ID·본문·보기·정답·해설·출처를 모두 보존한다", () => {
    const original = bank.filter(q => Number(q.id.split("-").at(-1)) <= 40);
    expect(original).toHaveLength(120);
    expect(createHash("sha256").update(JSON.stringify(original)).digest("hex")).toBe("040ca93d447371a7b25b211b885e1185d7e83d0cb474d7888caa7b22e99bab99");
  });
  it("요약 파일의 전체·과목·유형·family 수가 실제 JSON과 같다", () => {
    expect(summary).toMatchObject({total:1000, reviewed:1000, missing:0, concepts:170, numericVariants:830, numericFamilies:46});
    for (const subject of SUBJECTS) {
      const questions = bank.filter(q => q.subject === subject);
      expect(summary.subjects[subject]).toEqual({total:questions.length, concepts:questions.filter(q => !q.calculation).length, numericVariants:questions.filter(q => q.calculation).length});
    }
    expect(Object.values(summary.families).reduce((a,b) => a+b,0)).toBe(830);
  });
});

function halfUp(value: number, precision: number) {
  const scale = 10 ** precision;
  return Math.round((value + Number.EPSILON * Math.max(1, Math.abs(value))) * scale) / scale;
}
it("계산 표시의 양수 반올림 경계", () => {
  expect(halfUp(1.2345, 3)).toBe(1.235);
  expect(halfUp(1.2344, 3)).toBe(1.234);
  expect(halfUp(0.0005, 3)).toBe(0.001);
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
      case "mass-percent": computed=v[0]/v[1]*100; expect(unit).toBe("%"); break;
      case "molality": computed=v[0]/(v[1]/1000); expect(unit).toBe("mol/kg"); break;
      case "dilution-volume": computed=v[0]*v[1]/v[2]; expect(unit).toBe("mL"); break;
      case "ideal-volume": computed=v[0]*v[3]*v[1]/v[2]; expect(unit).toBe("L"); break;
      case "boyle-pressure": computed=v[0]*v[1]/v[2]; expect(unit).toBe("kPa"); break;
      case "charles-volume": computed=v[0]*v[2]/v[1]; expect(unit).toBe("L"); break;
      case "partial-pressure": computed=v[0]*v[1]/100; expect(unit).toBe("kPa"); break;
      case "gas-density": computed=v[0]/v[1]; expect(unit).toBe("g/L"); break;
      case "reaction-yield": computed=v[0]/v[1]*100; expect(unit).toBe("%"); break;
      case "neutralization-volume": computed=v[0]*v[1]/v[2]; expect(unit).toBe("mL"); break;
      case "mixture-molar-mass": computed=(v[0]*v[2]+v[1]*(100-v[2]))/100; expect(unit).toBe("g/mol"); break;
      case "solubility-mass": computed=v[0]*v[2]/v[1]; expect(unit).toBe("g"); break;
      case "isotope-mass": computed=v[1]-(v[1]-v[0])*v[2]/100; expect(unit).toBe("u"); break;
      case "faraday-charge": computed=v[0]*v[1]; expect(unit).toBe("C"); break;
      case "latent-heat": computed=v[0]*v[1]; expect(unit).toBe("J"); break;
      case "temperature-rise": computed=v[0]/v[1]/v[2]; expect(unit).toBe("K"); break;
      case "heat-release-rate": computed=v[0]/v[1]; expect(unit).toBe("kW"); break;
      case "combustion-energy": computed=v[0]*v[1]; expect(unit).toBe("kJ"); break;
      case "fire-load-density": computed=v[0]/v[1]; expect(unit).toBe("MJ/m²"); break;
      case "heat-flux": computed=v[0]/v[1]; expect(unit).toBe("kW/m²"); break;
      case "conduction-rate": computed=v[2]/v[3]*v[0]*v[1]; expect(unit).toBe("W"); break;
      case "convection-rate": computed=v[0]*v[1]*v[2]; expect(unit).toBe("W"); break;
      case "water-duration": computed=v[0]/v[1]; expect(unit).toBe("min"); break;
      case "foam-volume": computed=v[0]*v[1]; expect(unit).toBe("L"); break;
      case "foam-liquid-required": computed=v[0]/v[1]; expect(unit).toBe("L"); break;
      case "water-layer-volume": computed=v[0]*(v[1]/1000)*1000; expect(unit).toBe("L"); break;
      case "heat-use-efficiency": computed=v[0]/v[1]*100; expect(unit).toBe("%"); break;
      case "liquid-mass": computed=v[0]*v[1]; expect(unit).toBe("kg"); break;
      case "liquid-volume": computed=v[0]/v[1]; expect(unit).toBe("L"); break;
      case "thermal-volume-increase": computed=v[0]*v[1]*v[2]; expect(unit).toBe("L"); break;
      case "rectangular-volume": computed=v[0]*v[1]*v[2]*1000; expect(unit).toBe("L"); break;
      case "cylinder-volume": computed=v[2]*v[0]**2*v[1]*1000; expect(unit).toBe("L"); break;
      case "fill-percentage": computed=v[0]/v[1]*100; expect(unit).toBe("%"); break;
      case "headspace-volume": computed=v[0]-v[1]; expect(unit).toBe("L"); break;
      case "mass-trace-concentration": computed=v[0]/v[1]; expect(unit).toBe("mg/kg"); break;
      case "mixed-mass-percent": computed=(v[0]/100*v[1]+v[2]/100*v[3])/(v[1]+v[3])*100; expect(unit).toBe("%"); break;
      case "evaporation-concentration": computed=v[0]/(v[1]-v[2])*100; expect(unit).toBe("%"); break;
      case "recovery-percentage": computed=v[0]/v[1]*100; expect(unit).toBe("%"); break;
      case "density-unit-conversion": computed=v[0]*0.001/(0.01**3); expect(unit).toBe("kg/m³"); break;
      case "volume-ppm": computed=v[0]/100*1e6; expect(unit).toBe("ppm"); break;
      default: throw new Error(`Unknown formula ${kind}`);
    }
    expect(Number.isFinite(computed)).toBe(true);
    const expected = halfUp(computed, q.calculation!.precision ?? 3);
    expect(expected).toBeCloseTo(result, 10);
    const options = q.choices.map(option => {
      const match = option.match(/^([0-9.]+) (.+)$/)!;
      expect(match).not.toBeNull();
      expect(match[2]).toBe(unit);
      return Number(match[1]);
    });
    expect(options[q.answer - 1]).toBeCloseTo(expected, 10);
    expect(options.filter(n => Math.abs(n - expected) < 1e-8)).toHaveLength(1);
    expect(q.explanation).toContain("조건:");
  });
}
