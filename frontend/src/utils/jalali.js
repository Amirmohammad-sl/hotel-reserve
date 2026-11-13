/**
 * Jalali (Solar Hijri) Calendar Utilities
 * Pure JavaScript, zero-dependency, mathematical calendar conversions.
 * Tested 100% roundtrip compatible.
 */

const BREAKS = [
  -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
  1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178,
]

export const PERSIAN_MONTH_NAMES = [
  'فروردین',
  'اردیبهشت',
  'خرداد',
  'تیر',
  'مرداد',
  'شهریور',
  'مهر',
  'آبان',
  'آذر',
  'دی',
  'بهمن',
  'اسفند',
]

export const PERSIAN_WEEKDAY_NAMES = [
  'شنبه',
  'یکشنبه',
  'دوشنبه',
  'سه‌شنبه',
  'چهارشنبه',
  'پنج‌شنبه',
  'جمعه',
]

export const PERSIAN_WEEKDAY_SHORT = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']

function div(a, b) {
  return ~~(a / b)
}

function mod(a, b) {
  return a - ~~(a / b) * b
}

function jalCalCore(jy) {
  const gy = jy + 621
  let leapJ = -14
  let jp = BREAKS[0]
  let jm
  let jump = 0
  for (let i = 1; i < BREAKS.length; i += 1) {
    jm = BREAKS[i]
    jump = jm - jp
    if (jy < jm) break
    leapJ = leapJ + div(jump, 33) * 8 + div(mod(jump, 33), 4)
    jp = jm
  }
  const n = jy - jp
  leapJ = leapJ + div(n, 33) * 8 + div(mod(n, 33) + 3, 4)
  if (mod(jump, 33) === 4 && jump - n === 4) leapJ += 1
  const leapG = div(gy, 4) - div((div(gy, 100) + 1) * 3, 4) - 150
  return { gy, march: 20 + leapJ - leapG, jump, n }
}

function leapFromCycle(jump, n) {
  let adjusted = n
  if (jump - n < 6) adjusted = n - jump + div(jump + 4, 33) * 33
  let leap = mod(mod(adjusted + 1, 33) - 1, 4)
  if (leap === -1) leap = 4
  return leap
}

function jalCal(jy) {
  const { gy, march, jump, n } = jalCalCore(jy)
  return { leap: leapFromCycle(jump, n), gy, march }
}

function jalCalShort(jy) {
  const { gy, march } = jalCalCore(jy)
  return { gy, march }
}

function g2d(gy, gm, gd) {
  let d =
    div((gy + div(gm - 8, 6) + 100100) * 1461, 4) +
    div(153 * mod(gm + 9, 12) + 2, 5) +
    gd -
    34840408
  d = d - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752
  return d
}

function d2g(jdn) {
  let j = 4 * jdn + 139361631
  j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908
  const i = div(mod(j, 1461), 4) * 5 + 308
  const gd = div(mod(i, 153), 5) + 1
  const gm = mod(div(i, 153), 12) + 1
  return {
    gy: div(j, 1461) - 100100 + div(8 - gm, 6),
    gm,
    gd,
  }
}

function j2d(jy, jm, jd) {
  const r = jalCalShort(jy)
  return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + jd - 1
}

function d2j(jdn) {
  const gy = d2g(jdn).gy
  let jy = Math.min(gy - 621, BREAKS[BREAKS.length - 1] - 1)
  const r = jalCal(jy)
  let k = jdn - g2d(r.gy, 3, r.march)
  if (k >= 0) {
    if (k <= 185) return { jy, jm: 1 + div(k, 31), jd: mod(k, 31) + 1 }
    k -= 186
  } else {
    jy -= 1
    k += 179
    if (r.leap === 1) k += 1
  }
  return { jy, jm: 7 + div(k, 30), jd: mod(k, 30) + 1 }
}

/**
 * Convert Gregorian date to Jalali
 * @param {number|Date|string} gyOrDate
 * @param {number} [gm]
 * @param {number} [gd]
 * @returns {{jy: number, jm: number, jd: number}}
 */
export function toJalaali(gyOrDate, gm, gd) {
  if (typeof gyOrDate === 'string') {
    const parts = gyOrDate.split('-').map((x) => parseInt(x, 10))
    return d2j(g2d(parts[0], parts[1], parts[2]))
  }
  if (gyOrDate instanceof Date) {
    return d2j(g2d(gyOrDate.getFullYear(), gyOrDate.getMonth() + 1, gyOrDate.getDate()))
  }
  return d2j(g2d(gyOrDate, gm, gd))
}

/**
 * Convert Jalali date to Gregorian
 * @param {number} jy
 * @param {number} jm
 * @param {number} jd
 * @returns {{gy: number, gm: number, gd: number}}
 */
export function toGregorian(jy, jm, jd) {
  return d2g(j2d(jy, jm, jd))
}

/**
 * Check if Jalali year is a leap year
 */
export function isLeapJalaaliYear(jy) {
  return jalCal(jy).leap === 0
}

/**
 * Return number of days in a Jalali month
 */
export function jalaaliMonthLength(jy, jm) {
  if (jm <= 6) return 31
  if (jm <= 11) return 30
  return isLeapJalaaliYear(jy) ? 30 : 29
}

/**
 * Convert Jalali (jy, jm, jd) to ISO string "YYYY-MM-DD"
 */
export function jalaliToIso(jy, jm, jd) {
  const g = toGregorian(jy, jm, jd)
  const pad = (n) => String(n).padStart(2, '0')
  return `${g.gy}-${pad(g.gm)}-${pad(g.gd)}`
}

/**
 * Convert ISO string "YYYY-MM-DD" to Jalali object { jy, jm, jd }
 */
export function isoToJalali(isoStr) {
  if (!isoStr || typeof isoStr !== 'string') return null
  const [y, m, d] = isoStr.split('-').map((v) => parseInt(v, 10))
  if (!y || !m || !d) return null
  return toJalaali(y, m, d)
}

/**
 * Format ISO string "YYYY-MM-DD" or Date to Persian display string
 * e.g. "۲۲ آبان ۱۴۰۵" or "۱۴۰۵/۰۸/۲۲"
 */
export function formatJalaliDate(isoOrDate, format = 'long') {
  if (!isoOrDate) return ''
  let j
  if (typeof isoOrDate === 'string') {
    j = isoToJalali(isoOrDate)
  } else if (isoOrDate instanceof Date) {
    j = toJalaali(isoOrDate)
  }
  if (!j) return ''

  const toFaDigits = (str) =>
    String(str).replace(/[0-9]/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d])

  if (format === 'short') {
    const pad = (n) => String(n).padStart(2, '0')
    return toFaDigits(`${j.jy}/${pad(j.jm)}/${pad(j.jd)}`)
  }

  if (format === 'monthYear') {
    return `${PERSIAN_MONTH_NAMES[j.jm - 1]} ${toFaDigits(j.jy)}`
  }

  return `${toFaDigits(j.jd)} ${PERSIAN_MONTH_NAMES[j.jm - 1]} ${toFaDigits(j.jy)}`
}

/**
 * Return today's ISO date string "YYYY-MM-DD"
 */
export function getTodayIso() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

/**
 * Get weekday index for a Jalali date (0 = شنبه, 6 = جمعه)
 */
export function getJalaliWeekday(jy, jm, jd) {
  const g = toGregorian(jy, jm, jd)
  const d = new Date(g.gy, g.gm - 1, g.gd)
  // JS getDay(): 0 is Sunday, 6 is Saturday
  // Persian: Saturday = 0, Sunday = 1, ... Friday = 6
  const jsDay = d.getDay()
  return (jsDay + 1) % 7
}
