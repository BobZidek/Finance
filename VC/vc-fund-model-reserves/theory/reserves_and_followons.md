# VC Fund Reserves & Follow-On Strategy — Theory

## Why VC funds reserve capital rather than deploying it all upfront

A typical VC fund doesn't spend its entire committed capital on first checks. Instead, funds
**reserve a large share** (often 50%+ of the fund) specifically for **follow-on investments**
into portfolio companies that raise subsequent rounds and show enough traction to justify
doubling down. This fund reserves roughly 50% (15 initial checks at $1.5mm = $22.5mm, against
$60mm committed) for exactly this purpose.

The logic follows directly from the power law (see
[`VC/portfolio-power-law-model`](../portfolio-power-law-model)): since a small number of
portfolio companies will drive the overwhelming majority of fund returns, **maintaining or
increasing ownership in the apparent winners matters enormously more than spreading reserves
evenly**. A fund that can't follow its winners (because it deployed all its capital on first
checks) gets diluted out of its own best positions by later investors — leaving money on the
table in exactly the deals that matter most.

## Why follow-on capital returns a *lower* multiple than the initial check — for the *same* company

This project models each successful company's follow-on investment at a **materially lower
multiple** than its initial check (e.g. Company 15's initial $1.5mm check returns 40x, but its
$3mm follow-on check — invested two years later, once the company had already proven itself
and raised at a much higher valuation — returns only 6x). This isn't a modeling inconsistency;
it's a structural reality: **later-stage capital into an already-de-risked company is priced
at a higher valuation**, so the same eventual exit produces a smaller multiple on the
later, larger check, even though it generates far more *absolute* dollars ($18mm on the
follow-on vs. $60mm on the initial check, in Company 15's case). Both can be true
simultaneously: the follow-on decision was still an excellent one in dollar terms, even though
its *multiple* looks worse than the original bet.

## The no-hurdle waterfall — a genuine structural difference from PE funds

Unlike [`PE/fund-model-waterfall`](../fund-model-waterfall) (which models a European
whole-fund waterfall with an 8% preferred return and a GP catch-up), **this VC fund model uses
a straight no-hurdle waterfall**: 100% of distributions go to LPs until they've received back
all contributed capital, and then an **immediate 80/20 split** — no preferred return tier, no
catch-up. Many (though not all) venture funds use exactly this simpler structure, in contrast
to buyout funds, where a preferred return is closer to a market standard. Both are legitimate,
real-world fund structures — the difference matters for anyone comparing IRR/DPI figures
across a PE fund and a VC fund, since the waterfall mechanics themselves shift when carry
starts flowing.

## An honest caveat about this project's follow-on decisions

This model's follow-on capital was allocated to the **5 companies that happened to become the
biggest winners** — by construction, since the dataset was built to demonstrate the mechanics
clearly. In this project's run, those 5 companies (33% of the portfolio) generate **95.1% of
total fund proceeds**. **Real VCs don't have this foresight.** Follow-on decisions are made
under genuine uncertainty, using imperfect signals (revenue growth, retention, the quality of
the round the company is raising, competitive dynamics) — and even skilled investors get
follow-on decisions wrong some of the time, doubling down on companies that later stall and
passing on ones that later take off. This project demonstrates the **mechanics and potential
payoff of an effective reserve strategy**, not a claim that reserve deployment reliably works
out this well — see `ENHANCEMENTS.md` for how to model follow-on decisions under realistic
uncertainty instead of perfect hindsight.
