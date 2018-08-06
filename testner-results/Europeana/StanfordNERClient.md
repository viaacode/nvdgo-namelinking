## StanfordNERClient
| Accuracy   | Time    |   Total checked |
|:-----------|:--------|----------------:|
| 92.67%     | 19651ms |          451146 |

### Confusion Matrix
| Predict   |   LOCATION |      O |   PERSON |
|:----------|-----------:|-------:|---------:|
| Actual    |            |        |          |
| LOCATION  |       2207 |  12617 |     1295 |
| O         |       1290 | 408796 |     6879 |
| PERSON    |        247 |  10756 |     7059 |

### Overall Statistics
| Name                                   | Value             |
|:---------------------------------------|:------------------|
| Overall ACC                            | 0.92667           |
| Kappa                                  | 0.351             |
| Overall RACC                           | 0.88701           |
| Strength Of Agreement(Landis and Koch) | Fair              |
| Strength Of Agreement(Fleiss)          | Poor              |
| Strength Of Agreement(Altman)          | Fair              |
| Strength Of Agreement(Cicchetti)       | Poor              |
| TPR Macro                              | 0.50272           |
| PPV Macro                              | 0.66627           |
| TPR Micro                              | 0.92667           |
| PPV Micro                              | 0.92667           |
| Scott PI                               | 0.34822           |
| Gwet AC1                               | 0.9223            |
| Bennett S                              | 0.89              |
| Kappa Standard Error                   | 0.00343           |
| Kappa 95% CI                           | (0.34426,0.35773) |
| Chi-Squared                            | None              |
| Phi-Squared                            | None              |
| Cramer V                               | None              |
| Chi-Squared DF                         | 4                 |
| 95% CI                                 | (0.92591,0.92743) |
| Standard Error                         | 0.00039           |
| Response Entropy                       | 0.28181           |
| Reference Entropy                      | 0.46267           |
| Cross Entropy                          | 0.5               |
| Joint Entropy                          | None              |
| Conditional Entropy                    | None              |
| KL Divergence                          | 0.03733           |
| Lambda B                               | None              |
| Lambda A                               | None              |
| Kappa Unbiased                         | 0.34822           |
| Overall RACCU                          | 0.88749           |
| Kappa No Prevalence                    | 0.85333           |
| Mutual Information                     | None              |
| Overall J                              | (1.32243,0.44081) |

### Class Statistics
| Class   |     LOCATION |            O |       PERSON | Description                                                                                                                                                     |
|:--------|-------------:|-------------:|-------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |      0.96576 |      0.93008 |      0.95749 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |      0.13339 |      0.29661 |      0.37195 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |     44.74227 |     23.14028 |     33.34989 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |      0.03424 |      0.06992 |      0.04251 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |      0.35488 |      0.95262 |      0.44681 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |      0.22222 |      0.96285 |      0.42403 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |      0.16176 |      0.97331 |      0.40346 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |      0.41052 |      0.05408 |      0.53660 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |  13912.00000 |   8169.00000 |  11003.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |      0.86308 |      0.01959 |      0.60918 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |      0.03110 |      0.43047 |      0.02524 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   1537.00000 |  23373.00000 |   8174.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |      0.00353 |      0.68380 |      0.01887 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |      0.28410 |      0.96301 |      0.42557 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |      0.12500 |      0.92837 |      0.26906 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |     38.75311 |      1.43376 |     20.70689 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |      0.86614 |      0.06196 |      0.62090 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |      0.27291 |      0.39101 |      0.40370 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |      0.55838 |      0.51545 |      0.43816 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 435027.00000 |  34181.00000 | 433084.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |      0.96890 |      0.56953 |      0.97476 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |  16119.00000 | 416965.00000 |  18062.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 451146.00000 | 451146.00000 | 451146.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |      0.58948 |      0.94592 |      0.46340 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |      0.03573 |      0.92424 |      0.04004 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |      0.00030 |      0.88536 |      0.00135 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |      0.00048 |      0.88564 |      0.00136 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 433490.00000 |  10808.00000 | 424910.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |      0.99647 |      0.31620 |      0.98113 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 447402.00000 |  18977.00000 | 435913.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   3744.00000 | 432169.00000 |  15233.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |   2207.00000 | 408796.00000 |   7059.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |      0.13692 |      0.98041 |      0.39082 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
