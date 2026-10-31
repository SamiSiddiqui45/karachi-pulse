import { test,expect } from '@playwright/test';

test('dataset failure recovers on retry and filtered export contains the selected category',async({page})=>{
  let fail=true;
  await page.route('**/data/facilities.geojson',route=>fail?route.fulfill({status:503,body:'Unavailable'}):route.continue());
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Dataset request failed (503)');
  fail=false;
  await page.getByRole('button',{name:'Try again'}).click();
  await expect(page.getByText('1,004',{exact:true})).toBeVisible();
  await page.getByRole('checkbox',{name:/Hospital/}).check();
  const downloaded=page.waitForEvent('download');
  await page.getByRole('button',{name:/Export GeoJSON/}).click();
  const download=await downloaded;
  expect(download.suggestedFilename()).toBe('karachi-pulse-filtered.geojson');
  const stream=await download.createReadStream();
  const chunks:Buffer[]=[];
  for await(const chunk of stream!)chunks.push(Buffer.from(chunk));
  const data=JSON.parse(Buffer.concat(chunks).toString('utf8'));
  expect(data.type).toBe('FeatureCollection');
  expect(data.features).toHaveLength(467);
  expect(data.features.every((feature:{properties:{category:string}})=>feature.properties.category==='Hospital')).toBe(true);
});

test('geolocation denial keeps the explorer usable and empty search resets',async({page,context})=>{
  await context.clearPermissions();
  await page.addInitScript(()=>{
    Object.defineProperty(navigator,'geolocation',{value:{getCurrentPosition:(_success:unknown,failure:()=>void)=>failure()}});
  });
  await page.goto('/');
  await page.getByRole('button',{name:'Find facilities near me'}).click();
  await expect(page.getByRole('alert')).toContainText('Location permission unavailable');
  await page.getByLabel('Search facilities').fill('no-such-facility-12345');
  await expect(page.getByText('No facilities found')).toBeVisible();
  await page.getByRole('button',{name:'Reset',exact:true}).click();
  await expect(page.getByText('1004 of 1004 facilities displayed')).toBeVisible();
});
