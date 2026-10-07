# Publication and provenance notes

This is a curated public reading packet, not an export of an account or a
complete execution audit. It includes 43 source editorial artifacts. All draft
and clean-script bytes are preserved, including rejected versions. Five files
omit operational identifiers from metadata only; each is labeled and the
manifest records both source and published hashes. No dialogue, advice or
editorial reasoning was silently rewritten for publication.

Excluded: raw chat/tool transcripts, operational run ledgers, account links and
identifiers, bundle cover sheets, old archive manifests, ZIPs and duplicated
canon input files. Historical `/workspace/...` paths inside briefs identify
the original working context; they are not downloadable GitHub paths. Use this
packet's index for the corresponding published files.

The aggregate reading packet is generated from the unchanged six canon ledgers,
the two exact dialogue catalogs and the two latest clean scripts. It is a
convenience copy, not new authority. Authored chapter plans and implementation
reviews remain linked separately. Wording is preserved; relative Markdown link
targets are rebased for the packet location. The GDScript blocks are verbatim.

## Dispositions and disagreements

- Ivo's original Examiner acceptance predates Astra's findings and the Grok
  repair. It does not approve the original proposal. The controlling editorial
  decision is the [draft-2 call](ivo/astra/astra-final-call-draft-2.md).
- Ivo's [first Astra review](ivo/astra/astra-review-draft-1.md) is a Producer
  condensation/reformatting, despite an original “verbatim” claim. Only partial
  original excerpts were recoverable. The [correction record](ivo/closeout/PROVENANCE_CORRECTIONS.md)
  preserves this limit. The final call preserves wording but was not a native
  byte-exact message export.
- Nell's Examiner recommended READY WITH MINOR NOTES on draft 1. Astra held
  draft 3 on voice/payoff grounds after two repairs. This is a substantive
  editorial disagreement, not a demonstrated human playtest failure or a newly
  found runtime defect. The [final decision](nell/astra/ASTRA_FINAL_DECISION.txt)
  supersedes the downloaded run snapshot's earlier WAITING_FOR_ASTRA state.
  Both runs are closed; none of the embedded repair assignments is current.

## Process evidence limits

The Ivo repair pilot used one Sonnet consultation, two Grok writing turns
(initial revision plus one repair), one Examiner pass on draft 1 and two Astra
editorial reads. A later reread reconfirmed the acceptance. The Nell run used
one Sonnet consultation, three Grok writing turns (initial plus two repairs),
one Examiner pass on draft 1 and three Astra editorial reads.

Consultation length limits were exceeded: Ivo's body was counted at 747 words
against 600 requested; Nell's reported 617 exceeded 450 requested. Neither
overrun prompted an extra call. Exact billing and charged usage pools are not
verified. The compact evidence does not establish a complete command-level
audit of consultant activity.

Early Nell packaging had a stale self-hash and embedded archive-hash problem.
Those operational manifests are not republished as if valid. The final turn-3
ZIP CRC, SHA-256 and all 37 payload entries verified locally. The fresh
publication manifest never includes its own hash or claims to be an archive
hash. These checks establish artifact identity, not writing quality.

## Original archive identities

Archives remain local; this packet publishes their selected text contents.

| Source | SHA-256 |
| --- | --- |
| Original Ivo review bundle | `4c233e381db400cd9c3895e592eec91875b2bd9cc77174d8af55dcb0615f10b7` |
| Final Grok Ivo repair bundle | `9b96ad35d4bcd7e19356ebeae068f31319cf59b75f373891d8e061acd1222118` |
| Nell turn-3 review bundle | `00aac2c804e70a54a2b45769be570f85ad62b9014e9eff8880d75815c48c04e1` |
