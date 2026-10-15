# Bioinformatics notes

Bioinformatics (AKA computational biology, quantitative systems biology, theoretical / mathematical biology, or biostatistics) is a sub-field of biology that uses computation instead of lab experiments. Experimental biology is often known as **wet lab**, whereas computational biology is known as **dry lab**.

## Central Dogma

One process, shared by every cellular organism on Earth:

```
DNA --(transcription)--> mRNA --(translation)--> Protein
```

| Step | Input                   | Output  | Name          |
| ---- | ----------------------- | ------- | ------------- |
| 1    | Gene (segment of DNA)   | mRNA    | Transcription |
| 2    | mRNA (aka "transcript") | Protein | Translation   |

Proteins do the actual work of the cell: signaling, stimulus response, metabolism, regulation, structure.

DNA being used to make a product (mRNA or protein) is also called **gene expression**. Different gene expression patterns can signal biological differences between cells (e.g. a gene expressed higher/lower in cancerous vs. healthy cells).

## Cell Biology Basics

The smallest independently functioning unit of life. Handles growth, metabolism, and reproduction. Can be a standalone organism (bacteria) or a building block of a multicellular one (humans).

### Prokaryotic vs. Eukaryotic

|                           | Prokaryotic                   | Eukaryotic              |
| ------------------------- | ----------------------------- | ----------------------- |
| Nucleus                   | No                            | Yes                     |
| Membrane-bound organelles | No                            | Yes                     |
| DNA                       | Free-floating, often circular | Enclosed in nucleus     |
| Size                      | Smaller                       | Larger                  |
| Examples                  | Bacteria, archaea             | Protists, yeast, humans |

### Key Organelles

| Organelle    | Function                                                                                                                      |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Nucleus      | Holds DNA/chromosomes; site of transcription. Eukaryotes only.                                                                |
| Nucleolus    | Combines ribosomal RNA and proteins into ribosomal subunits.                                                                  |
| Ribosome     | Site of translation (protein assembly). Found in both prokaryotes and eukaryotes.                                             |
| Rough ER     | Lined with ribosomes; handles protein processing and folding.                                                                 |
| Smooth ER    | Not lined with ribosomes; handles lipid synthesis.                                                                            |
| Golgi body   | Modifies and packages proteins and lipids.                                                                                    |
| Mitochondria | Generates ATP via cellular respiration (including the Krebs/citric acid cycle). Has its own DNA and replicates independently. |

### Plant vs. Animal Cells

|                 | Plant | Animal |
| --------------- | ----- | ------ |
| Cell wall       | Yes   | No     |
| Central vacuole | Large | No     |
| Chloroplasts    | Yes   | No     |
| Centrosomes     | No    | Yes    |
| Lysosomes       | No    | Yes    |

### Cellular Processes

| Term       | Definition                                                                           |
| ---------- | ------------------------------------------------------------------------------------ |
| Metabolism | Converting nutrients into energy (ATP).                                              |
| Catabolism | Breaking down molecules to release energy.                                           |
| Anabolism  | Using energy to build molecules.                                                     |
| Cell cycle | The stages a cell goes through between divisions.                                    |
| Mitosis    | Cell division producing two identical cells, each with 2 copies of every chromosome. |
| Meiosis    | Cell division producing gametes (egg/sperm), each with 1 copy of every chromosome.   |

## Gene Expression & Regulation

### Stability

| Molecule | Stability                                          |
| -------- | -------------------------------------------------- |
| DNA      | Stable, persists                                   |
| mRNA     | Semi-transient - produced, floats around, degrades |
| Protein  | Semi-transient, but usually longer-lived than mRNA |

Production and degradation of both mRNA and protein are modeled as random (stochastic) processes.

### One Gene, Many Proteins

Useful simplification: 1 gene → 1 mRNA → 1 protein.

Not literally true. The same gene can produce multiple protein variants (**isoforms**, usually similar function) via:

- Different splicing of the mRNA (**alternative splicing**)
- Different transcription start/stop sites
- Extra processing after translation

Because of this simplification, biologists are often loose with naming. Example: "p53" can refer to the protein, the gene, or the mRNA - context tells you which. (Technically precise: gene = `TP53`.)

### Gene Regulation

Some proteins (**transcription factors**) bind DNA near another gene (or their own) and make transcription easier or harder. This is **gene regulation**.

- Can form large, complex **gene regulatory networks** (genes regulating genes regulating genes).
- Malfunctioning regulation → disease (e.g. cancer).
- Gene expression + gene regulation, scaled to networks of hundreds/thousands of genes, already explains a lot of cellular complexity.

## DNA Structure

- A **nucleic acid**: a chain of nucleotides.
- Double stranded.
- 4 bases: **A**denine, **T**hymine, **C**ytosine, **G**uanine.

### Base Pairing

| Base | Pairs with |
| ---- | ---------- |
| A    | T          |
| T    | A          |
| C    | G          |
| G    | C          |

Each pair across the two strands = a **base pair**. One strand implies the other, so a DNA sequence is normally written as just one strand's letters.

## Transcription

RNA polymerase binds DNA, unzips it, and reads one strand, building a complementary strand of mRNA base by base:

| DNA base read | mRNA base added |
| ------------- | --------------- |
| G             | C               |
| C             | G               |
| T             | A               |
| A             | U               |

Copying a complementary sequence also copies the information encoded in it.

### mRNA vs. DNA

|              | DNA         | mRNA             |
| ------------ | ----------- | ---------------- |
| Strands      | Double      | Single (usually) |
| Bases        | A, T, C, G  | A, U, C, G       |
| Also made of | Nucleotides | Nucleotides      |

## Translation

mRNA attaches to a ribosome. Its sequence is read in triplets called **codons**; each codon specifies one amino acid, or a start/stop signal.

- Some codons differing by one letter still code for the same amino acid (**synonymous**).
- Some codons differing by one letter code for a *different* amino acid (**missense**) → possibly a different, more/less functional protein. A one-letter DNA difference between two people can therefore be biologically inconsequential or consequential depending on which codon position it hits.

Amino acids are strung together, then folded/processed into the final 3D protein structure. A visualization can be found [here](https://www.youtube.com/watch?v=gG7uCskUOrA).

## Proteins

- Chains of amino acids, folded into a 3D structure.
- Functions: catalyzing metabolic reactions, structural support, signaling, regulating cellular processes, and (as transcription factors) regulating gene expression.

## Epigenetics

Explains how cells with identical DNA (e.g. liver, hair, brain, skin cells) end up biologically different.

- In complex organisms, DNA is organized into a 3D structure (**chromosomes** - 23 pairs in humans).
- DNA can be wrapped tightly or loosely around **histone** proteins.

| Wrapping | Accessibility                | Result                            |
| -------- | ---------------------------- | --------------------------------- |
| Loose    | Accessible to RNA polymerase | Gene can be transcribed/expressed |
| Tight    | Inaccessible                 | Gene is silenced                  |

- Different cell types have different epigenetic regulation profiles → different genes expressed → different proteins → different biological roles, despite (nearly) identical DNA.
- The process of turning generic embryonic stem cells into specialized cell types is **cell differentiation** (aka cell fate determination). The exact mechanism is still not fully understood.

## Statistics

A way of putting a number on coincidences, using probability theory.

### The Coin Problem

Is a coin fair (50/50) or biased toward one side? Flip it and count heads:

| Flips | Result     | Chance a fair coin does this (or the all-tails equivalent) |
| ----- | ---------- | ---------------------------------------------------------- |
| 3     | All heads  | 25%                                                        |
| 5     | All heads  | 6.25%                                                      |
| 10    | All heads  | ~0.2%                                                      |
| 20    | All heads  | ~0.0002%                                                   |
| 1,000 | All heads  | ~10^-301                                                   |

No row ever reaches 0%. A fair coin *can* land heads 1,000 times in a row; it would just take an extreme coincidence. Absolute certainty that a coin is biased is impossible. What statistics offers instead is the size of the coincidence.

### Worked Example

1. Assume nothing unusual is going on: the coin is fair. This is the **null hypothesis**.
2. Run the experiment: 5 flips → 5 heads, 0 tails.
3. Ask: if the coin is fair, how likely is a result at least this extreme by chance alone?

```
P(5 heads) = 0.5 × 0.5 × 0.5 × 0.5 × 0.5 = 0.5^5 = 0.03125
P(5 heads or 5 tails) = 0.5^5 × 2 = 0.0625
```

The ×2 counts the other extreme: 5 tails would be just as surprising.

So a fair coin produces a result this lopsided 6.25% of the time. Is the coin biased? Unknown, but now the coincidence has a number.

### Terms

| Term                   | Definition                                                                                   | Coin example         |
| ---------------------- | -------------------------------------------------------------------------------------------- | -------------------- |
| Null hypothesis        | The assumption that nothing unusual is going on.                                             | The coin is fair.    |
| Alternative hypothesis | Any hypothesis other than the null.                                                          | The coin is biased.  |
| p-value                | Probability of a result at least as extreme as the observed one, assuming the null is true. | 0.0625 (5/5 heads)   |

Smaller p-value → bigger coincidence required to explain the result with the null.

### Applied to Gene Expression

Same reasoning, different coin. The dataset: lung tissue samples from patients with idiopathic pulmonary fibrosis (IPF) vs. healthy controls, with expression measurements for ~18,000 genes.

Every gene varies randomly across samples. Suppose one gene's measurements look lower in IPF samples than in controls:

- **Null hypothesis**: both groups come from the same underlying distribution; the gap is random variation.
- **Alternative hypothesis**: there is a real difference in expression between conditions.
- **p-value**: the probability of a gap at least this large between the groups if the null were true.

Repeat for every gene, and each one gets a number on how much of a coincidence its difference would be.
