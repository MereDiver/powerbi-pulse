# PULSE implementation notes

This document records the implementation found during the public-repository cleanup and the intentional behavioral changes made for the first public proof-of-concept release.

## As-found implementation

PULSE was a two-cell Classic Jupyter Notebook application:

- Cell 1 rendered the green PULSE/stethoscope header and used the global Classic Notebook `Jupyter.notebook` JavaScript API to restart a run.
- Cell 2 contained configuration, authentication, Power BI REST discovery, widget UI, report embedding, dynamic cell creation, page/visual inspection, data export, result classification, and Excel generation.
- `InteractiveLoginAuthentication` from `powerbiclient` authenticated embedded reports.
- A separate MSAL `ConfidentialClientApplication` used `APP_ID`, `TENANT_ID`, and `SECRET_VALUE` for workspace/report discovery through the Power BI REST API.
- A notebook prompt selected between location-specific direct/VPN modes and automatic PAC proxy discovery. The PAC test incorrectly required an unauthenticated request to an authenticated Power BI endpoint to return HTTP 200.
- Selected reports were embedded into dynamically generated notebook cells. A final generated cell enumerated pages and visuals, exported summarized data, classified export failures and all-blank columns, measured export duration, and generated a timestamped workbook in `Results/`.
- The notebook depended directly on the Classic Notebook frontend (`Jupyter.notebook.*`) and is not compatible with the Notebook 7 frontend.
- Legacy Windows launchers contained network-share and machine-specific paths, decrypted a local `.env` with a hard-coded AES key, wrote to a fixed log path, and launched a bundled Python interpreter. BurntToast and VBS files duplicated this launcher experiment.

## Identified defects and risks

- The launcher and encryption artifacts exposed private paths, a local username, and reusable key material.
- The runtime `.env` contained real credential values and was not protected by a repository ignore file.
- Duplicate workspace/report display labels could overwrite each other in a dictionary.
- Report-derived Python variable names could collide; report names containing backticks or other special characters could also break dynamically generated JavaScript/Python cells.
- REST calls had no timeout and incomplete exception handling.
- The PAC connectivity test treated the expected unauthenticated response as a proxy failure.
- The page-switch comparison returned on its first successful fetch, so it did not verify a change.
- A one-row data export was excluded from blank-column checking.
- A run containing only slow exports did not create a workbook because workbook creation was gated on errors/warnings.
- `Skipped_Visuals` was omitted whenever `Slow_Exports` existed because the sheets were mutually exclusive.
- The completion message referenced a deployment-specific Windows results location.
- Notebook outputs and execution counters were present in the publication candidate.

## Public POC architecture decision

The public reference uses one delegated interactive authentication object. `powerbiclient` 3.1.1's authentication base exposes `get_access_token()`, and the library itself uses the resulting Power BI token for REST calls needed to obtain report embed URLs. PULSE reuses that token for workspace/report discovery and passes the same authentication object to each embedded report.

This removes the local client secret and confidential-client configuration. An optional `PULSE_TENANT_ID` can constrain sign-in to one tenant; otherwise the library's default authority is used. This choice still requires live validation in the user's tenant because tenant policy, consent, licensing, and workspace permissions vary. The authentication boundary is intentionally small so another organization-approved pattern can replace it.

Optional PAC support is isolated in `proxy_support.py`, disabled by default, and lazy-loads PyPAC only when requested. The normal path respects the host's standard networking configuration.

## Behavioral changes

The cleanup makes these intentional behavior changes:

1. Workspace discovery and report embedding reuse a single delegated interactive Power BI token.
2. Network choices are generic (`Standard connection` and `Automatic PAC proxy`) rather than location/deployment specific.
3. An HTTP response from the Power BI API, including an authentication response, proves PAC transport connectivity; HTTP 200 is no longer required before authentication.
4. REST requests use a configurable timeout and report actionable request failures.
5. Duplicate report labels receive deterministic numeric suffixes and generated report variables use stable numeric names.
6. Dynamic cell contents are JSON-escaped before insertion, and report titles are HTML-escaped before Markdown rendering.
7. The hard-coded visual skip list is replaced by the optional generic `PULSE_SKIP_VISUALS_JSON` configuration, defaulting to an empty list.
8. Blank checking includes one-row exports and reports exports with headers but no data rows as warnings.
9. Duration uses a monotonic high-resolution timer.
10. A workbook is generated for errors, warnings, slow exports, or explicitly skipped visuals. Slow and skipped sheets can coexist.
11. Generated workbook links use a Jupyter-served relative path and UI text is platform-neutral.
12. Repeated-run cleanup guards against stale dynamic cell indices and always removes the spinner when analysis completes.
13. My Workspace is represented as a first-class workspace option and uses the ungrouped reports endpoint with `group_id=None` for embedding.
14. Visual discovery assigns a distinct pending sentinel because `powerbiclient` 3.1.1 otherwise uses an empty list for both its waiting state and a valid empty-page response. Empty pages are now logged separately from unresponsive pages.

## Compatibility boundary

This release intentionally targets Classic Notebook 6.5.7. Migrating the dynamic UI to Notebook 7 or JupyterLab requires replacing the frontend JavaScript API and is outside this cleanup.
