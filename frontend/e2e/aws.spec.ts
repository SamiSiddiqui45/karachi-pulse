import { test,expect } from '@playwright/test';
test('Amazon Location style and map tiles load through the restricted public map key',async({page})=>{
  test.setTimeout(60000);
  test.skip(!process.env.PULSE_AWS,'Requires configured real AWS map');
  let descriptors=0,tiles=0;
  const failures:number[]=[];
  page.on('response',response=>{
    const url=response.url();
    if(!url.includes('maps.geo.ap-south-1.amazonaws.com'))return;
    if(response.status()>=400)failures.push(response.status());
    if(url.includes('style-descriptor')&&response.ok())descriptors++;
    if(url.includes('/tiles/')&&response.ok())tiles++;
  });
  await page.goto('/');
  await expect(page.locator('.cluster-count').first()).toBeVisible({timeout:20000});
  await expect.poll(()=>descriptors).toBeGreaterThan(0);
  await expect.poll(()=>tiles,{timeout:20000}).toBeGreaterThan(0);
  await expect(page.locator('.map-error')).toHaveCount(0);
  expect(failures).toEqual([]);
});
