# Calibration: a heuristic, not a ratchet

Chesterton's Fence is an argument for *investigation*, not for freezing the system. Do not let it become a lazy defense of the status quo:

- If archaeology shows the fence is obsolete, remove it confidently — keeping known-dead code has real costs (it miseducates every future reader, including you).
- Scale rigor to blast radius. A magic number in a payment path deserves full archaeology; an oddly named local variable in a test helper does not. Spend investigation effort where removal could hurt.
- Genuinely new code you wrote this session, with no history, has no fences. This discipline applies to *inherited* behavior.
- If the user has already done the archaeology and tells you the reason, believe them and record it — don't re-litigate.
