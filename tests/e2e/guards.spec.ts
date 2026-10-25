import { expect, test } from "@playwright/test";

test("입력 실패 경고는 유지하고 상단 상시 면책 배너는 만들지 않는다", async ({page}) => {
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => { throw new DOMException("quota", "QuotaExceededError"); };
  });
  await page.goto("");
  await expect(page.getByRole("alert")).toContainText("기록을 저장하지 못했습니다");
  await expect(page.locator(".criteria-note")).toHaveCount(0);
  await expect(page.getByLabel("학습 기준")).toHaveCount(0);
  await page.getByRole("button", {name:"문제풀이 시작하기", exact:true}).click();
  await expect(page.locator(".question-stem")).toBeVisible();
  await expect(page.getByRole("alert")).toContainText("기록을 저장하지 못했습니다");
  await expect(page.locator(".criteria-note")).toHaveCount(0);
});

test("Space의 IME·반복·수정키와 열린 메뉴 보호, 실제 키 누름/해제", async ({page}) => {
  await page.goto("");
  await page.getByRole("button", {name:"모의시험 시작하기", exact:true}).click();
  await page.getByRole("group", {name:"답안 선택"}).getByRole("button").first().click();
  const counter = page.locator(".question-counter strong");
  for (const extra of [{isComposing:true}, {repeat:true}, {altKey:true}, {ctrlKey:true}, {metaKey:true}]) {
    await page.locator(".question-stem").evaluate((el, init) => el.dispatchEvent(new KeyboardEvent("keydown", {code:"Space", key:" ", bubbles:true, ...init})), extra);
    await expect(counter).toHaveText("01");
  }
  const opener = page.getByRole("button", {name:"메뉴 열기"});
  if (await opener.isVisible()) {
    await opener.click();
    await page.locator(".question-stem").evaluate(el => el.dispatchEvent(new KeyboardEvent("keydown", {code:"Space", key:" ", bubbles:true})));
    await expect(counter).toHaveText("01");
    await page.getByRole("button", {name:"메뉴 닫기"}).click();
  }
  await page.locator(".question-stem").focus();
  await page.keyboard.down("Space");
  await page.keyboard.up("Space");
  await expect(counter).toHaveText("02");
  await expect(page.locator(".explanation")).toHaveCount(0);
  await expect(page.locator(".criteria-note")).toHaveCount(0);
});
