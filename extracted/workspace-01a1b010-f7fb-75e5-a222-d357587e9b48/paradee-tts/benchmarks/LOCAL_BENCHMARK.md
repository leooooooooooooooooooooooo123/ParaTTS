# Local benchmark

Measured on Linux-6.1.189+-x86_64-with-glibc2.41, Python 3.12.16, 2 visible CPUs.

**Local results only; not Render results.**

- Cold startup: 0.4908 s
- Model bytes: 8462119
- Peak combined RSS: 412.71 MB (10 ms polling)
- Installed site-packages: 496024616 bytes

| Run | Characters | Seconds | Audio seconds | RTF | Bytes |
|---|---:|---:|---:|---:|---:|
| short #1 | 25 | 2.8396 | 2.125 | 1.32941 | 102044 |
| short #2 | 25 | 2.8406 | 2.125 | 1.32984 | 102044 |
| medium #1 | 107 | 2.975 | 8.325 | 0.35601 | 399644 |
| medium #2 | 107 | 2.9394 | 8.325 | 0.3515 | 399644 |
| long #1 | 348 | 3.4801 | 22.8 | 0.15213 | 1094444 |
| long #2 | 348 | 3.4643 | 22.8 | 0.1515 | 1094444 |