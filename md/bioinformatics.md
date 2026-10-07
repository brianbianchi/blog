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

## Fundamentals

### Cells

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

| Organelle    | Function                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------------- |
| Nucleus      | Holds DNA/chromosomes; site of transcription. Eukaryotes only.                                 |
| Nucleolus    | Combines ribosomal RNA and proteins into ribosomal subunits.                                   |
| Ribosome     | Site of translation (protein assembly). Found in both prokaryotes and eukaryotes.              |
| Rough ER     | Lined with ribosomes; handles protein processing and folding.                                  |
| Smooth ER    | Not lined with ribosomes; handles lipid synthesis.                                             |
| Golgi body   | Modifies and packages proteins and lipids.                                                     |
| Mitochondria | Generates ATP via the Krebs (citric acid) cycle. Has its own DNA and replicates independently. |

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

## Gene Expression

The central dogma process (DNA → mRNA → protein) is also called **gene expression**: using information encoded in DNA to make a product (mRNA or protein). Different gene expression patterns can signal biological differences between cells (e.g. a gene expressed higher/lower in cancerous vs. healthy cells).

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

- Different splicing of the mRNA
- Different transcription start/stop sites
- Extra processing after translation

Because of this simplification, biologists are often loose with naming. Example: "p53" can refer to the protein, the gene, or the mRNA - context tells you which. (Technically precise: gene = `TP53`.)

### Gene Regulation

Some proteins (**transcription factors**) bind DNA near another gene (or their own) and make transcription easier or harder. This is **gene regulation**.

- Can form large, complex **gene regulatory networks** (genes regulating genes regulating genes).
- Malfunctioning regulation → disease (e.g. cancer).
- Gene expression + gene regulation, scaled to networks of hundreds/thousands of genes, already explains a lot of cellular complexity.

## DNA (Deeper Dive)

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

## Transcription (Deeper Dive)

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

## Translation (Deeper Dive)

mRNA attaches to a ribosome. Its sequence is read in triplets called **codons**; each codon specifies one amino acid (or start/stop).

- Some codons differing by one letter still code for the same amino acid.
- Some codons differing by one letter code for a *different* amino acid → possibly a different, more/less functional protein. (Relevant later for the GWAS project: a one-letter DNA difference between two people can be inconsequential or consequential depending on this.)

Amino acids are strung together, then folded/processed into the final 3D protein structure.

## Proteins (Deeper Dive)

- Chains of amino acids, folded into a 3D structure.
- Alternate splicing of mRNA before translation can also produce different isoforms.
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
