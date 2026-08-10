# Manual Power BI integration checklist

No live disposable Power BI tenant was available during the public-repository cleanup. Run this checklist in a non-sensitive test workspace before publishing a release or changing authentication, proxy, timing, or notebook UI behavior. Record environment and package versions without recording tokens or private identifiers.

- [ ] **Interactive authentication:** With `PULSE_TENANT_ID` empty, sign in through the browser and confirm no token or account details appear in notebook output. Repeat with a permitted tenant ID.
- [ ] **Workspace discovery:** Confirm My Workspace and all shared workspaces expected for the signed-in user appear once and are sorted. Confirm My Workspace remains usable when shared workspace discovery is unavailable.
- [ ] **Report discovery:** Select one and multiple workspaces. Confirm reports are mapped to the correct workspace and duplicate display names remain separately selectable.
- [ ] **Report embedding:** Select one and multiple reports, including a name containing punctuation. Confirm each report embeds under the correct title and renders before analysis.
- [ ] **Page discovery:** Confirm visible and hidden pages returned by `get_pages()` are handled as expected and a report with no usable pages does not stop other reports.
- [ ] **Empty page:** Include a page containing no visuals. Confirm it logs `Empty page skipped` without consuming all timeout retries or preventing later pages from running.
- [ ] **Visual discovery:** Confirm visuals belong to the requested page after page switching. Exercise a slow-rendering page and verify retries/log messages.
- [ ] **Healthy visual:** Export a supported visual with populated data and confirm it counts as successful without appearing in `Errors_Warnings`.
- [ ] **Problematic visual:** Use a reproducibly broken visual or denied export and confirm an error row contains the report, page, visual, type, and safe error text.
- [ ] **Blank-data warning:** Test both a header-only export and a populated export with one entirely blank column. Confirm warnings; verify a slicer is not checked.
- [ ] **Slow-export detection:** Temporarily lower `PULSE_SLOW_EXPORT_THRESHOLD_SECONDS`; confirm a workbook is created even when the run contains only successful-but-slow visuals. Confirm rows over the highlight threshold are red.
- [ ] **Skipped visuals:** Add a local `PULSE_SKIP_VISUALS_JSON` exact-match rule. Confirm only that visual is skipped and `Skipped_Visuals` coexists with other sheets.
- [ ] **Excel output:** Open the timestamped workbook from `Results/` and from the notebook link. Verify sheet names, columns, warning text, timing, and formatting.
- [ ] **Repeated runs:** Run a second analysis without restarting the kernel. Confirm old generated cells and selectors are removed, selections are fresh, and no stale report variables/results leak into the run.
- [ ] **Optional PAC mode:** On a system with a safe test PAC, select automatic PAC mode and complete discovery/embedding. Confirm an authenticated endpoint's 401/403 during the transport probe is not treated as a proxy failure. Switch back to standard mode and confirm only PULSE-managed proxy variables are restored.
