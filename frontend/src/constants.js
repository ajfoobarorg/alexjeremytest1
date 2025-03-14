// Get all country codes and names using Intl.DisplayNames
const regionNames = new Intl.DisplayNames(['en'], { type: 'region' });

// List of ISO 3166-1 alpha-2 country codes
const allCountryCodes = [
  'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
  'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BV', 'BR',
  'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX',
  'CC', 'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DJ', 'DM',
  'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF',
  'TF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN',
  'GW', 'GY', 'HT', 'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM',
  'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV',
  'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT',
  'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM',
  'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK',
  'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU',
  'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC',
  'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS', 'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ',
  'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM',
  'TC', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY', 'UZ', 'VU', 'VE', 'VN', 'VG', 'VI',
  'WF', 'EH', 'YE', 'ZM', 'ZW'
];

export const COUNTRIES = allCountryCodes
  .map(code => {
    try {
      return {
        code,
        name: regionNames.of(code)
      };
    } catch (e) {
      console.warn(`Error processing country ${code}:`, e);
      return null;
    }
  })
  .filter(country => country !== null)
  .sort((a, b) => a.name.localeCompare(b.name));

// Function to format timezone offset for display
function formatOffset(timeZone) {
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone,
    timeZoneName: 'longOffset'
  });
  const parts = formatter.formatToParts(new Date());
  return parts.find(p => p.type === 'timeZoneName').value;
}

// Generate timezone list with IANA names
export const TIMEZONES = Intl.supportedValuesOf('timeZone')
  .map(zone => {
    try {
      const offset = formatOffset(zone);
      const [continent, ...locationParts] = zone.split('/');
      const location = locationParts.join('/').replace(/_/g, ' ');
      
      return {
        value: zone,  // IANA timezone name (e.g., "America/New_York")
        label: `${location} (${offset})`,  // e.g., "New York (GMT-04:00)"
        group: continent,  // e.g., "America"
        offset  // For sorting
      };
    } catch (e) {
      console.warn(`Error processing timezone ${zone}:`, e);
      return null;
    }
  })
  .filter(tz => tz !== null)
  .sort((a, b) => {
    // Sort by offset first, then by location name
    if (a.offset !== b.offset) {
      return a.offset.localeCompare(b.offset);
    }
    return a.label.localeCompare(b.label);
  });

// Group timezones by continent/region
export const TIMEZONE_GROUPS = TIMEZONES.reduce((groups, tz) => {
  if (!groups[tz.group]) {
    groups[tz.group] = [];
  }
  groups[tz.group].push(tz);
  return groups;
}, {}); 