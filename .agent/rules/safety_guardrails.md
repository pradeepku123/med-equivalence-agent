# Drug Safety Guardrails
**Version:** 1.0.0 | **Created:** 2026-08-21

This rule governs mandatory safety checks before presenting any medicine substitution recommendation.

---

## 1. Schedule Classification (MANDATORY CHECK)

Every result MUST display the drug's Schedule classification:

| Schedule | Description | Substitution Warning |
|----------|-------------|---------------------|
| **OTC** | Over-the-counter, no prescription needed | ✅ Safe to suggest substitution |
| **Schedule H** | Prescription required | ⚠️ "Requires valid prescription. Consult your doctor before switching." |
| **Schedule H1** | Enhanced prescription (habit-forming / high-risk) | 🔴 "This is a controlled substance. Substitution requires specialist consultation." |
| **Schedule X** | Narcotic / psychotropic | 🚫 "Do NOT substitute without explicit medical authorization." |

---

## 2. Narrow Therapeutic Index (NTI) Drug Flag

NTI drugs have a small margin between therapeutic and toxic dose. Substitution requires extra caution.

**MANDATORY NTI Flag for these drug classes:**
- Digoxin, Warfarin, Lithium, Phenytoin, Carbamazepine, Theophylline, Levothyroxine, Cyclosporine, Tacrolimus, Methotrexate, Vancomycin

If a queried drug is NTI:
```
🔴 NTI DRUG WARNING: <drug_name> has a Narrow Therapeutic Index.
Bioequivalence between generic and brand may vary.
Generic substitution MUST be supervised by a physician with therapeutic drug monitoring.
DO NOT self-substitute this medication.
```

---

## 3. Anti-substitution Rules

**NEVER suggest substitution without explicit disclaimer for:**
- Insulin formulations (different concentrations / delivery systems)
- Blood thinners (INR monitoring required)
- Immunosuppressants (organ transplant patients)
- Antiepileptics (seizure threshold sensitive)
- Psychiatric medications (titration required)

---

## 4. Pediatric & Geriatric Safety Flag

- If the user mentions a child (< 12 years) or elderly (> 65 years): **Always recommend consulting a paediatric/geriatric pharmacist**
- Flag any age-specific dosing changes in the generic vs. brand formulation

---

## 5. Duplicate Therapy Warning

If a user queries multiple medicines in the same session:
- Check for **duplicate active ingredients** across different brand names
- Alert: `⚠️ Duplicate Therapy Risk: {drug_A} and {drug_B} both contain {ingredient}. Taking both may cause an overdose.`

---

## 6. Mandatory Disclaimer (EVERY RESPONSE)

Every response presenting medicine information MUST end with:
```
⚕️ Disclaimer: This information is for educational purposes only and does not constitute medical advice.
Always consult a licensed pharmacist or qualified physician before changing, substituting, or discontinuing any medication.
Generic equivalents contain the same active ingredient but may differ in formulation, excipients, or bioavailability.
```
