"""Official 2024 Lok Sabha election manifesto sources.

URLs verified directly against each party's own domain. BJP's site has been
observed to hang/time out for automated fetches from some networks (likely
bot mitigation); ingestion treats each source independently and skips any
that fail rather than blocking the whole corpus or fabricating content.
"""

MANIFESTOS = [
    {
        "party_id": "bjp",
        "party_name": "Bharatiya Janata Party (BJP)",
        "title": "Sankalp Patra 2024 (Modi Ki Guarantee)",
        "url": "https://www.bjp.org/files/2024-04/Modi-Ki-Guarantee-Sankalp-Patra-English_2.pdf",
        "hue": "#e0a455",
    },
    {
        "party_id": "inc",
        "party_name": "Indian National Congress (INC)",
        "title": "Nyay Patra 2024",
        "url": "https://manifesto.inc.in/assets/Congress-Manifesto-English-2024-Dyoxp_4E.pdf",
        "hue": "#56c8d0",
    },
    {
        "party_id": "cpim",
        "party_name": "Communist Party of India (Marxist) (CPI(M))",
        "title": "Election Manifesto 2024",
        "url": "https://cpim.org/wp-content/uploads/old/documents/election_manifesto_english_april_2024.pdf",
        "hue": "#e0768f",
    },
]
