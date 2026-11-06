# Compatibility and deployment verification

Date: **2026-11-06**. Environment: Linux x86_64, Python 3.12.16, two visible CPUs. Official Paradee 1.2.1 pinned at `c2789ef9abf54a9384eef89cc7de3f1afe5ad01d`.

| Capability | Local result | Render Free |
|---|---|---|
| Real int8 ONNX generation | Passed | Not deployed |
| `af_heart` | Passed | Not deployed |
| `bf_isabella` | Passed | Not deployed |
| `am_puck` | Passed | Not deployed |
| `bm_fable` | Passed | Not deployed |
| WAV structure/playback/download | Passed | Not deployed |
| MP3 encoding | Passed with `lameenc` | Not deployed |
| Concurrent requests | Passed, bounded to one inference slot | Not deployed |
| Validation/traversal/model failure | Passed | Not deployed |
| Automated tests | 9 passed | Not run |
| Combined RAM | 412.71 MB observed peak | Unknown |
| Public HTTPS URL | Not applicable | None |

## Performance

Cold startup 0.4908 seconds. Short requests averaged approximately 2.84 seconds; medium 2.96 seconds; long requests producing 22.8 seconds of audio averaged 3.47 seconds. These timings include isolated phonemization and model lifecycle overhead. Exact samples are in `benchmarks/local-results.json`.

## Render qualification

**Render Free compatibility is unverified, not guaranteed.** The local combined peak is below 512 MB, but cgroup accounting, dependencies and runtime conditions may differ. Free hosting may sleep and has ephemeral storage and limited CPU. A successful deployment must be followed by real all-voice generation, memory inspection and public URL testing before updating this report.

No deployment URL or result is fabricated.
