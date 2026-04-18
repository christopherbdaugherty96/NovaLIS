# Live Test Checklist — Cap 55: weather_snapshot
Phase 5 of 6 · Priority: Medium (read_only_network)

## Pre-conditions
- [ ] Location is configured in Nova settings (or auto-detected)
- [ ] Network available

## Test 1 — Basic weather
1. Type: `weather`
2. ✅ Weather widget appears
3. ✅ Shows temperature, conditions, location
4. ✅ Loads in reasonable time

## Test 2 — Question phrasing
1. Type: `what's the weather today`
2. ✅ Same weather widget

## Test 3 — Forecast
1. Type: `weather forecast`
2. ✅ Forecast or current conditions returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 55
python scripts/certify_capability.py lock 55
```
