import {expect, test} from "@playwright/test";

test("1,000문항 실제 목록의 50페이지와 마지막 추가 문항에 접근한다", async ({page}) => {
  await page.goto("");
  await expect(page.locator(".bank-summary")).toContainText(/등록\s*1000문항/);
  const menu = page.getByRole("button", {name:"메뉴 열기"});
  if (await menu.isVisible()) await menu.click();
  await page.getByRole("navigation").getByRole("button", {name:"문제은행 관리",exact:true}).click();
  await expect(page.locator(".rules-details")).toContainText("개념형 170개");
  await expect(page.locator(".rules-details")).toContainText("숫자 변형 830개 / 46유형");
  const next = page.locator(".pagination").getByRole("button", {name:"다음",exact:true});
  for (let i=1; i<50; i++) await next.click();
  await expect(page.locator(".pagination")).toContainText("50 / 50");
  await expect(next).toBeDisabled();
  await expect(page.locator(".bank-row")).toHaveCount(20);
  await expect(page.locator(".bank-row").last()).toContainText("HM-3-325");
  await page.locator(".bank-row").last().locator("summary").click();
  await expect(page.locator(".bank-row").last().locator(".explanation")).toContainText("210 ppm");
  await page.getByLabel("문항 검색", {exact:true}).fill("HM-3-325");
  await expect(page.locator(".bank-row")).toHaveCount(1);
  await expect(page.locator(".bank-filter")).toContainText("1문항");
});
