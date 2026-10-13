---
name: roman-poster-icloud-eviction
description: ~/Documents/로마콘크리트_3D is iCloud-synced; files get evicted (dataless) within ~40 min and re-download can stall for a long time
metadata:
  node_type: memory
  type: project
  originSessionId: 73df8d3b-73af-481e-9f8b-64064c56fc53
  modified: 2026-10-12T11:11:46.300Z
---

On 2026-10-12, mid-run, macOS evicted 632 files under `~/Documents/로마콘크리트_3D/narrative_benchmark_20261007`: scripts, every `.blend`, review_loop and out/print. Some had been written only 10–40 minutes earlier. Disk had 33 GB free, so the eviction was not caused by low space.

- **Symptoms:** `ls -lO` shows `compressed,dataless`. `cat` or Blender on such a file blocks with no error, and commands time out at 120 s.
- **Why the download stalled:** bird was busy applying a huge iCloud trash deletion, and `brctl download` plus parallel `cat` moved about 7 small files in 10 minutes.

**Why:** Long pipelines (Blender, compose, print) silently hang on dataless inputs. The real copy stays in iCloud, so nothing is lost, but work stalls.

**How to apply:**
- Before running a stage, check its inputs with `find <dir> -flags +dataless`.
- Keep working copies of the active blend, scripts and outputs in the session scratchpad or another non-iCloud folder. Copy deliverables back afterwards.
- Scripts I wrote can be recovered from the session transcript (Write inputs and Bash heredocs).
- Related: [[roman-poster-v12-color-pipeline]]
