# Direct dependency license review

MIT is appropriate for PULSE's original repository code: the declared direct dependencies use permissive licenses compatible with distribution alongside MIT-licensed code. PULSE does not vendor or modify their source. This is an informational review, not legal advice; release maintainers should re-check package metadata and transitive dependencies when versions change.

| Dependency | Declared license |
|---|---|
| Jupyter Notebook | BSD-3-Clause |
| powerbiclient | MIT |
| Requests | Apache-2.0 |
| pandas | BSD-3-Clause |
| ipywidgets | BSD-3-Clause |
| IPython | BSD-3-Clause |
| nest_asyncio | BSD-2-Clause |
| openpyxl | MIT |
| PyPAC | Apache-2.0 |
| python-dotenv | BSD-3-Clause |

`jupyter-client`, `ipykernel`, and `traitlets` are explicit Classic Notebook compatibility constraints rather than application imports; each is BSD-licensed at the pinned version.

