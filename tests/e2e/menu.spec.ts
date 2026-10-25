import { expect, test, type Page } from "@playwright/test";

async function inViewport(page: Page, selector: string) {
  const rect = await page.locator(selector).boundingBox();
  expect(rect).not.toBeNull();
  expect(rect!.y).toBeGreaterThanOrEqual(0);
  expect(rect!.y + rect!.height).toBeLessThanOrEqual(page.viewportSize()!.height);
}

// Real CDP touch events go through Chromium's native scrolling pipeline.
// Reading scrollTop below is an assertion only, never a programmatic scroll.
async function swipe(page: Page, upwards: boolean, distance = 140) {
  const cdp = await page.context().newCDPSession(page);
  const height = page.viewportSize()!.height;
  const start = upwards ? height - 70 : 80;
  const end = upwards ? start - distance : start + distance;
  await cdp.send("Input.dispatchTouchEvent", {type:"touchStart", touchPoints:[{x:130,y:start}]});
  for (let step = 1; step <= 10; step++) {
    await cdp.send("Input.dispatchTouchEvent", {type:"touchMove", touchPoints:[{x:130,y:start + (end-start)*step/10}]});
    await page.waitForTimeout(15);
  }
  await cdp.send("Input.dispatchTouchEvent", {type:"touchEnd", touchPoints:[]});
  await page.waitForTimeout(100);
  await cdp.detach();
}

for (const [width, height, enlarged] of [[390,480,false], [740,360,false], [390,480,true]] as const) {
  for (const input of ["wheel", "touch"] as const) {
    test(`${width}×${height} ${enlarged ? "200% 글자" : "기본 글자"} 메뉴 ${input} 상하 접근`, async ({browser}, testInfo) => {
      const context = await browser.newContext({viewport:{width,height}, hasTouch:true, isMobile:true});
      const page = await context.newPage();
      await page.goto(testInfo.project.use.baseURL!);
      if (enlarged) await page.addStyleTag({content:".sidebar { font-size: 200%; } .sidebar button, .sidebar p, .sidebar small { font-size: inherit !important; }"});
      await page.getByRole("button", {name:"메뉴 열기"}).click();
      // Wait for the menu's actual transition rather than clicking in flight.
      await expect(page.locator(".sidebar")).toHaveClass(/open/);
      await page.waitForTimeout(350);
      const scroll = () => page.locator(".sidebar").evaluate(el => el.scrollTop);
      const start = await scroll();
      const move = async (delta: number) => {
        if (input === "touch") await swipe(page, delta > 0, Math.abs(delta));
        else { await page.mouse.move(130, height/2); await page.mouse.wheel(0, delta); await page.waitForTimeout(100); }
      };
      const reach = async (selector: string) => {
        for (let i=0; i<35; i++) {
          const rect = (await page.locator(selector).boundingBox())!;
          if (rect.y >= 0 && rect.y + rect.height <= height) break;
          await move(rect.y < 0 ? -100 : 100);
        }
        await inViewport(page, selector);
      };
      await reach('.sidebar button:has-text("학습 기록 백업")');
      expect(await scroll()).toBeGreaterThan(start);
      expect(await page.evaluate(() => window.scrollY)).toBe(0);
      const download = page.waitForEvent("download");
      await page.getByRole("button", {name:"학습 기록 백업"}).click();
      expect((await download).suggestedFilename()).toContain("hazardous-materials");
      await reach('.sidebar button:has-text("데이터 초기화")');
      await page.getByRole("button", {name:"데이터 초기화", exact:true}).click();
      await expect(page.getByRole("dialog")).toBeVisible();
      await page.getByRole("button", {name:"돌아가기", exact:true}).click();
      for (let i=0; i<35 && await scroll() > 2; i++) await move(-140);
      expect(await scroll()).toBeLessThanOrEqual(2);
      await inViewport(page, '.sidebar nav button[aria-label="학습 대시보드"]');
      await page.getByRole("navigation").getByRole("button", {name:"학습 대시보드"}).click();
      await expect(page.locator(".sidebar")).not.toHaveClass(/open/);
      await expect(page.getByRole("heading", {name:"위험물산업기사 필기 CBT", exact:true})).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      await page.screenshot({path:testInfo.outputPath("menu-return-home.png"), fullPage:true});
      await context.close();
    });
  }
}
