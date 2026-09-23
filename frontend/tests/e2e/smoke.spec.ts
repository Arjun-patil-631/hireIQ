import { test, expect } from '@playwright/test'

test('dashboard loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Interview Intelligence Dashboard' })).toBeVisible()
  await expect(page.getByText('Candidate evaluations')).toBeVisible()
})

test('rubric editor loads', async ({ page }) => {
  await page.goto('/rubrics')
  await expect(page.getByRole('heading', { name: 'Rubric Builder' })).toBeVisible()
  await expect(page.locator('.yaml-editor')).toContainText('criteria:')
})
