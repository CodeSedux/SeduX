import assert from 'node:assert/strict';
import test from 'node:test';

import { getConsentRows, normalizeConsentKey } from '../src/views.js';

test('consent labels map to stable keys for UI updates', () => {
  assert.equal(normalizeConsentKey('Device controls'), 'device_controls');
  assert.equal(normalizeConsentKey('Voice processing'), 'voice_processing');

  const rows = getConsentRows({ consent: { devices: true, voice: false } });
  assert.deepEqual(rows.slice(0, 2).map((row) => row.key), ['device_controls', 'voice_processing']);
  assert.equal(rows[0].checked, true);
  assert.equal(rows[1].checked, false);
  assert.equal(rows[2].key, 'screen_access');
});
