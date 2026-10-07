# Provenance corrections — ivo-grok-repair-20261006-01

These corrections are added at closeout. No earlier file was overwritten. Earlier files keep their original bytes and hashes.

## 1. `astra/astra-review-draft-1.md` is NOT verbatim
- SHA256 `364f1e348a6c5a33b0f63955c2ed978e8a3d6050d7b5d1a684861fd47eaad630`.
- What it is: a faithful but condensed and reformatted brief of Astra's 7:15 PM CT review, written by the Producer. It drops Astra's introduction, the three source URLs and the closing instructions, and it restructures the text under headings.
- Wrong labels to disregard: `COVER_NOTE_TURN2.md` says it was "saved verbatim", and the Producer's chat messages said "word for word" and "verbatim". The correct label is "condensed/reformatted brief, not verbatim".
- The Writer's turn-2 work used this brief as its binding input.

## 2. Original message preservation (partial)
- `astra/astra-review-draft-1-original-excerpts.md`, SHA256 `037bcdd4a513cebfc577434d76c6a254cf881c49c8dd1f8e332a2fbd80d44ce5`.
- The transcript reader is the only native export available to the Producer, and it leaves out a middle section of the original message (part of R2 and the start of R3). No complete raw copy was found on the Producer's computer.
- So that file holds the opening and closing parts exactly as the reader displayed them. It is partial and must not be treated as the full original.

## 3. Sonnet consultation length overrun
- The consultation was asked to stay at or under 600 words.
- Astra counted the advice body at 747 whitespace-delimited words. The whole file `consultation/consultation-advice.md`, including the Producer's metadata header, is 781 words (`wc -w`).
- The overrun is recorded here. No extra call was spent to shorten it.

## 4. Starrett catalog link
- Astra could not load the Starrett catalog p.411 link cited in draft-2 §2.7.
- Astra found that Starrett's inspection-products article and the Kemet page support the general split between reference and working surfaces.
- The draft bytes stay unchanged, as Astra instructed.

## 5. Astra's final call file
- `astra/astra-final-call-draft-2.md`, SHA256 `a3fe8849505758222fac6cc3502ccb2a0cf70db212fde9342d91d21cf1b2008e`.
- The Producer copied it from the message text with the wording unedited. It is not a byte-exact native export.
