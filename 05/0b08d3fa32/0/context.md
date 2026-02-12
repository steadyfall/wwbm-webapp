# Session Context

## User Prompts

### Prompt 1

Review this plan thoroughly before making any code changes. 
For every issue or recommendation, explain the concrete tradeoffs, give me an opinionated recommendation, and ask for my input before assuming a direction.

My engineering preferences (use these to guide your recommendations):
- ﻿﻿DRY is important-flag repetition aggressively.
﻿﻿- Well-tested code is non-negotiable; I'd rather have too many tests than too few.
﻿﻿- I want code that's "engineered enough" - not under-engineere...

### Prompt 2

"ARCH-01 notes a potential naming collision between your auth app and Django's built-in django.contrib.auth. The app's AppConfig.name may need to be something like "trivivo_auth" or
  "player_auth" to avoid registry conflicts — worth verifying before that issue is worked." - add this as a note to ARCH-01.

