# Probability, From Coin Flips to Bell Curves

Probability is a number between 0 and 1 that describes how likely something is. A probability of 0 means it cannot happen, and a probability of 1 means it is certain. The same value can be written three ways:

| Decimal | Fraction | Percent |
| ------- | -------- | ------- |
| 0.25    | 1/4      | 25%     |
| 0.5     | 1/2      | 50%     |
| 0.9     | 9/10     | 90%     |

P(A) means "the probability of event A." For example, P(rain) = 0.3 means a 30% chance of rain.

## Experimental probability

One way to find a probability is to repeat an experiment and count the results:

```
P(A) = times A happened / total trials
```

Here are the results of a simulated coin, counting tails:

| Flips | Share of tails |
| ----- | -------------- |
| 10    | 0.3000         |
| 50    | 0.3800         |
| 100   | 0.4300         |
| 500   | 0.4640         |
| 1,000 | 0.4950         |
| 5,000 | 0.5144         |

Small experiments can land far from the expected 0.5, but larger ones tend to get closer. This is the law of large numbers: the more trials you run, the closer the experimental result tends to get to the true probability.

## Theoretical probability

When every outcome is equally likely, a probability can be found without an experiment:

```
P(A) = favorable outcomes / possible outcomes
```

The set of all possible outcomes is called the sample space, written S (some books use Ω). For one die, S = {1, 2, 3, 4, 5, 6}.

| Experiment    | Event     | Favorable | Possible | Probability |
| ------------- | --------- | --------- | -------- | ----------- |
| Roll a die    | Roll a 4  | 1         | 6        | 1/6         |
| Roll a die    | Roll odd  | 3         | 6        | 1/2         |
| Draw a card   | 7 of hearts | 1       | 52       | 1/52        |
| Draw a card   | Any king  | 4         | 52       | 1/13        |

The complement of an event A is the event that A does not happen. It is written Aᶜ, and some books use A' or Ā. One of the two must occur, so their probabilities add up to 1:

```
P(Aᶜ) = 1 - P(A)
```

For example, a bag holds 3 red, 2 blue, and 5 green marbles. If B is the event of drawing blue, then P(B) = 2/10 and P(Bᶜ) = 1 - 2/10 = 4/5.

## "And" and "or"

Suppose a made-up survey asks 100 people whether they like basketball and soccer:

|                     | Likes soccer | Does not like soccer | Total |
| ------------------- | ------------ | -------------------- | ----- |
| Likes basketball    | 15           | 33                   | 48    |
| Does not like basketball | 27      | 25                   | 52    |
| Total               | 42           | 58                   | 100   |

- **And** means both things are true. P(basketball and soccer) = 15/100 = 3/20.
- **Or** means at least one is true. P(basketball or soccer) counts everyone except the 25 who like neither.

Probability often uses symbols for these words, borrowed from set theory:

| Word | Symbol | Name         | Written  | Meaning                  |
| ---- | ------ | ------------ | -------- | ------------------------ |
| And  | ∩      | Intersection | A ∩ B    | In both A and B          |
| Or   | ∪      | Union        | A ∪ B    | In A, in B, or in both   |

The "or" in probability includes the case where both are true. A person who likes both sports still counts toward P(basketball ∪ soccer).

Adding the two totals counts the 15 people who like both sports twice, so they are subtracted once:

```
P(A ∪ B) = P(A) + P(B) - P(A ∩ B)

P(basketball ∪ soccer) = (48 + 42 - 15) / 100 = 75/100 = 3/4
```

## Conditional probability

Conditional probability is the chance of B, given that A already happened. It is written P(B | A). Knowing that A happened narrows the group being considered to only the cases where A is true.

```
P(B | A) = number of cases with both A and B / number of cases with A
```

Here is a made-up survey of 30 students:

|        | Likes school | Dislikes school | Total |
| ------ | ------------ | --------------- | ----- |
| Female | 10           | 4               | 14    |
| Male   | 9            | 7               | 16    |
| Total  | 19           | 11              | 30    |

What is the probability a student likes school, given that the student is female? Only the Female row matters. It has 14 students, and 10 of them like school, so the answer is 10/14 = 5/7.

Compare that with the whole group, where the probability is 19/30. The extra information changes the answer.

## The multiplication rule

To find the chance of two things both happening, multiply. The method depends on whether the first event changes the odds of the second.

| Type        | Meaning                                    | Formula                           |
| ----------- | ------------------------------------------ | --------------------------------- |
| Independent | The first event does not affect the second | P(A ∩ B) = P(A) × P(B)            |
| Dependent   | The first event changes the second         | P(A ∩ B) = P(A) × P(B &#124; A)   |

A die roll and a coin flip are independent:

```
P(roll a 3 ∩ flip tails) = 1/6 × 1/2 = 1/12
```

Drawing two cards without putting the first one back is dependent. After a king is drawn, 3 kings remain in 51 cards:

```
P(two kings in a row) = 4/52 × 3/51 = 1/221 ≈ 0.0045
```

A simulation of 200,000 two-card draws gave 0.00445, which is very close.

## Permutations

A permutation is an arrangement where order matters. To count them, multiply the number of choices for each position. The letters A, B, and C can be arranged 3 × 2 × 1 = 6 ways:

```
ABC  ACB  BAC  BCA  CAB  CBA
```

That countdown multiplication is called a factorial, written with an exclamation point:

| n  | 1 | 2 | 3 | 4  | 5   | 6   |
| -- | - | - | - | -- | --- | --- |
| n! | 1 | 2 | 6 | 24 | 120 | 720 |

Sometimes only some positions are filled. The number of ways to arrange r items chosen from n is written nPr, which is also the label on most calculators:

```
nPr = n! / (n - r)!
```

| Problem                                 | Calculation  | Result  |
| --------------------------------------- | ------------ | ------- |
| 1st, 2nd, and 3rd place from 10 runners | 10 × 9 × 8   | 720     |
| Lock with 3 different numbers from 0-59 | 60 × 59 × 58 | 205,320 |

## Combinations

A combination is a selection where order does not matter. A team of Alice, Bob, and Carol is the same as a team of Carol, Alice, and Bob.

To count combinations, start with the permutations, then divide out the repeats. Each group of r items can be arranged r! ways. The result is written nCr and read "n choose r." Textbooks often write it as n stacked above r inside parentheses, and some use C(n, r):

```
nCr = n! / ((n - r)! × r!)
```

Choosing 3 letters from A through E gives 60 permutations. Each group appears 6 times, so there are 60 / 6 = 10 combinations.

Combinations are useful for "exactly this many" problems. Suppose a team of 6 is picked at random from 7 kids and 11 adults. There are 18C6 = 18,564 possible teams. The number of teams with exactly 1 kid is:

```
7C1 × 11C5 = 7 × 462 = 3,234

P(exactly 1 kid) = 3,234 / 18,564 ≈ 0.1742
```

Repeating this for every number of kids gives the full picture:

| Kids on the team | Possible teams | Probability |
| ---------------- | -------------- | ----------- |
| 0                | 462            | 0.0249      |
| 1                | 3,234          | 0.1742      |
| 2                | 6,930          | 0.3733      |
| 3                | 5,775          | 0.3111      |
| 4                | 1,925          | 0.1037      |
| 5                | 231            | 0.0124      |
| 6                | 7              | 0.0004      |

## The normal distribution

Die rolls and cards can be listed one by one. Height cannot, because there are infinitely many possible values between 1.6 and 1.7 meters. A quantity like this is called continuous.

The chance of any one exact value is 0, since nobody is exactly 1.65000... meters tall. Instead, the question is the chance of landing in a range. On a probability curve, that chance equals the area under the curve over that range, and the total area is 1.

The most famous of these curves is the normal distribution, or bell curve. Two numbers define it:

| Symbol | Name               | What it controls        |
| ------ | ------------------ | ----------------------- |
| μ      | Mean               | Where the center is     |
| σ      | Standard deviation | How spread out it is    |
| σ²     | Variance           | The standard deviation squared, another measure of spread |

Every normal distribution follows the empirical rule:

| Distance from the mean        | Share of values |
| ----------------------------- | --------------- |
| Within 1 standard deviation   | About 68%       |
| Within 2 standard deviations  | About 95%       |
| Within 3 standard deviations  | About 99.7%     |

## Z-scores

A z-score says how many standard deviations a value is from the mean:

```
z = (x - μ) / σ
```

Z-tables list the share of values below a given z-score. To find the share above it, subtract from 1.

Suppose lifespans in a group are normally distributed with a mean of 68 years and a standard deviation of 10. What fraction live past 76?

```
z = (76 - 68) / 10 = 0.8
```

| Age | Z-score | Share below | Share above |
| --- | ------- | ----------- | ----------- |
| 68  | 0       | 0.5000      | 0.5000      |
| 73  | 0.5     | 0.6915      | 0.3085      |
| 76  | 0.8     | 0.7881      | 0.2119      |
| 78  | 1       | 0.8413      | 0.1587      |
| 88  | 2       | 0.9772      | 0.0228      |

The table shows that about 21% live past 76.

## The binomial distribution

The binomial distribution counts the successes in a set number of tries. It applies when:

- the number of tries is fixed
- each try has two outcomes, success or failure
- the chance of success stays the same on every try

A random variable is a number determined by a chance outcome, usually named with a capital letter. Then P(X = 2) means "the probability that X equals 2."

Roll a die 4 times and let X be the number of threes. What is P(X = 2)?

One specific order, such as three, three, other, other, has probability 1/6 × 1/6 × 5/6 × 5/6. The 2 threes can land in 4C2 = 6 different positions, so multiply by 6. In general, with n tries, k successes, and a success chance of p:

```
P(X = k) = nCk × p^k × (1 - p)^(n - k)

P(X = 2) = 6 × (1/6)² × (5/6)² ≈ 0.1157
```

| k (threes in 4 rolls) | P(X = k) |
| --------------------- | -------- |
| 0                     | 0.4823   |
| 1                     | 0.3858   |
| 2                     | 0.1157   |
| 3                     | 0.0154   |
| 4                     | 0.0008   |

The expected value is the long-run average, written E(X):

```
E(X) = n × p
```

Over 4 rolls, E(X) = 4 × 1/6 ≈ 0.67 threes. No single game can produce 0.67 threes, but that is the average over many games.

## The geometric distribution

The geometric distribution asks a different question: how many tries until the first success? The conditions match the binomial, except the number of tries is not fixed.

Let X be the number of tries needed. To get the first success on try k, there must be k - 1 failures followed by one success:

```
P(X = k) = (1 - p)^(k - 1) × p

E(X) = 1 / p
```

Suppose you roll a pair of dice until you get doubles. There are 6 doubles among the 36 possible rolls, so p = 1/6.

```
P(X = 4) = (5/6)³ × 1/6 ≈ 0.0965

P(X < 3) = 1/6 + (5/6 × 1/6) ≈ 0.3056
```

The expected wait is E(X) = 1 / (1/6) = 6 rolls. A simulation of 20,000 games averaged 5.98.

| Roll of first doubles | Exact probability | Simulated |
| --------------------- | ----------------- | --------- |
| 1                     | 0.1667            | 0.1661    |
| 2                     | 0.1389            | 0.1359    |
| 3                     | 0.1157            | 0.1190    |
| 4                     | 0.0965            | 0.0951    |
| 5                     | 0.0804            | 0.0826    |
| 6                     | 0.0670            | 0.0673    |
| 7                     | 0.0558            | 0.0555    |
| 8                     | 0.0465            | 0.0469    |

The most likely single outcome is getting doubles on the first roll, even though the average wait is 6 rolls. A few long streaks without doubles pull the average up.
