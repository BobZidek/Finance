# Liquidation Preferences — Theory

## Why this is the single most important term sheet clause

Valuation and ownership % get most of the attention in a financing negotiation, but
**liquidation preference terms determine how proceeds actually get split at exit** — and for
any exit below a "great" outcome, the preference structure can matter far more than the
headline valuation. A founder who negotiated a high valuation but conceded participating
preferred can end up with dramatically less than a founder who took a lower valuation with
clean non-participating terms, depending on how the exit plays out.

## Structure 1: 1x Non-Participating Preferred

The investor gets the **greater of** their liquidation preference OR converting to common and
taking their pro-rata share:

```
Payout = max(Liquidation Preference, Ownership % x Exit Value)
```

This is the founder-friendliest common structure: at low exit values the preference protects
the investor's downside (never receiving less than they put in, ahead of common), while at
high exit values the investor simply converts to common and shares proportionally like
everyone else — **never double-dipping**.

**Conversion crossover**: the exit value at which converting becomes better than taking the
preference is exactly where `Ownership % x Exit Value = Preference`, i.e.
`Exit Value = Preference / Ownership %`. In this project: `$15mm / 20% = $75mm` — confirmed
exactly by the model's output (`NonParticipating_SeriesB_mm` is flat at $15mm through $75mm,
then grows in lockstep with 20% of exit value beyond that).

## Structure 2: 1x Participating Preferred (Uncapped)

The investor gets their preference **first**, and **then also** participates pro-rata in the
remaining proceeds as if converted — a genuine double-dip:

```
Payout = Preference + Ownership % x (Exit Value − Preference)     [if Exit Value > Preference]
Payout = Exit Value                                                [if Exit Value <= Preference]
```

This is strictly better for the investor than non-participating at every exit value above the
preference (and identical below it) — which is exactly why it's more investor-friendly and why
sophisticated founders resist it. In this project's output, **participating uncapped payouts
exceed non-participating payouts by a growing margin as exit value rises** (e.g. $42mm vs.
$30mm at a $150mm exit) — that gap is common/founder value transferred to the investor purely
by the structure, not by the ownership %.

## Structure 3: 1x Participating Preferred with a Cap

A negotiated middle ground: participation is capped at a multiple of invested capital (3x
here — investor payout can never exceed `$15mm x 3.0 = $45mm`), **but** once that cap would
produce a *worse* outcome than simply converting to common, the investor converts instead
(preferred stock terms never force an investor to take *less* than straight conversion):

```
Payout = max(Ownership % x Exit Value, min(Participating Uncapped Payout, Cap))
```

This project's output shows this exact three-regime behavior: **payout tracks the uncapped
participating line until the cap binds (~$200mm exit value here)**, **stays flat at the $45mm
cap** for a range of exit values above that, and then **eventually converges back to the
non-participating (straight as-converted) line** at very high exit values (by $350mm, the
capped structure pays exactly what non-participating would: $70mm) — because at that point,
20% of a huge exit value simply exceeds the $45mm cap, and the investor is always guaranteed
at least the as-converted alternative.

## Why founders should care about all three, not just the headline preference multiple

At a modest exit (say $30mm here), the three structures diverge only modestly ($15mm vs.
$18mm vs. $18mm) — participation barely matters yet, since the preference alone is still
binding. At a large exit ($150mm), the gap widens meaningfully ($30mm vs. $42mm vs. $42mm) —
**$12mm that would otherwise go to common/founders instead goes to the investor purely from
the participation term**, with no change in ownership %. This is exactly why "what's the
liquidation preference" is an insufficient question in a term sheet negotiation — "is it
participating, and is there a cap" determines the actual economics far more than the headline
multiple alone.
