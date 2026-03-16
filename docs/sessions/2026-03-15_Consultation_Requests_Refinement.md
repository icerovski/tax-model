# Session Log: 2026-03-15 - Refinement of Professional Consultation Requests

## Objectives
- Refine the formal Requests for Professional Tax Advice (Bulgaria, USA, BVI) to adopt a first-person perspective.
- Strengthen the "Commercial Substance" narrative by explicitly stating the consulting service is specialized "US PV/BESS market research" and "finding clients for traders".
- Introduce a forward-looking clause regarding the intention to potentially invest directly in a US-based operating business in the future.
- Draft business-casual cover letters for engaging the respective tax advisors.

## Technical Changes
- **docs/requests/tax_request_bulgaria.md**: 
    - Rewritten in the first person. 
    - Added specific PV/BESS market research and client sourcing context to validate the 25% statutory deduction and mitigate hidden-employment scrutiny.
    - Added a question on how future direct US investments might affect Bulgarian tax treatment.
- **docs/requests/tax_request_usa.md**:
    - Rewritten in the first person.
    - Added the PV/BESS research and client sourcing context to confirm it does not trigger an ETBUS (Engaged in Trade or Business in the US) nexus.
    - Added an inquiry about the structural precautions needed for future direct US investments.
- **docs/requests/tax_request_bvi.md**:
    - Rewritten in the first person.
    - Added PV/BESS context for Economic Substance (ES) classification.
    - Added future US investment plans.
- **docs/requests/cover_letter.md**:
    - Created two distinct business-casual cover letter drafts (Option 1 for the US advisor, Option 2 for the Bulgarian advisor) designed to be sent with the corresponding Scope of Inquiry appended.

## Logic & Decisions
- **Narrative Framing:** By specifying "US PV/BESS Market Research" and "finding clients for traders", we provide a highly credible commercial rationale for utilizing a US-domiciled entity. This matching of the entity's jurisdiction to the subject matter of the research provides a strong defense against transfer pricing or sham-structure accusations during a potential NRA audit.
- **Future-Proofing:** Asking the advisors about future direct US investments now ensures the chosen structure won't become a liability if the PE strategy pivots from pure passive trading to active business acquisition.

## Next Steps
- The client will copy the cover letters and scopes of inquiry into emails and dispatch them to the selected tax professionals.
- Await the legal memorandums and adjust the `engine.py` logic if the advisors contradict any of the model's current premises.
