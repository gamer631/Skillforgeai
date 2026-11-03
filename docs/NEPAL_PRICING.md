# Nepal-first pricing and unit economics

## Pricing principles

1. Keep a useful free tier.
2. Price in NPR and disclose limits before a user reaches them.
3. Avoid unlimited expensive model usage on low-cost plans.
4. Route simple tasks to lower-cost models and reserve stronger models for tasks that need them.
5. Offer student discounts/scholarships only after unit economics are measured.
6. Never sell or imply a certificate, accreditation, or professional qualification; this product is an AI assistant.

## Initial pricing hypotheses (not launch commitments)

| Plan | Indicative price | Initial allowance idea |
|---|---:|---|
| Free | NPR 0 | Small daily message allowance; standard model only |
| Student | NPR 199/month | Higher monthly message allowance and longer context |
| Plus | NPR 499/month | More usage and access to stronger models |
| Team | From NPR 1,499/month | Shared billing/admin only after team features exist |

All allowances must be finalised only after provider cost, tax, payment fees, support costs, and abuse scenarios are measured. Do not advertise “unlimited” usage unless there is a defensible fair-use policy and cost ceiling.

## Cost-control requirements before paid beta

- Persist provider-reported input/output token usage where supported.
- Set per-user daily/monthly request and token budgets.
- Apply max input and output token limits server-side.
- Store model, provider, latency, and estimated cost per request.
- Route requests by task class and plan.
- Add anomaly alerts and global provider spend caps.
- Prevent retry loops and duplicate billing.
- Show a usage meter to users.

## Validation plan

Interview at least 20 target users in Nepal. Ask what they currently use, which workflows they would pay for, how often they use AI, their preferred payment method, and what price they can sustain. Offer a small paid pilot before committing to full subscription tiers.

## Revenue model

- Freemium individual plans
- Low-cost student subscription
- Higher-usage professional plan
- Later, team plans and API access

Do not make revenue forecasts until active use, retention, average token usage, and model costs are observed.
