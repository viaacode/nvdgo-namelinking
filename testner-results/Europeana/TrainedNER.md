## TrainedNER
| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 90.60%     | 445691ms |          451146 |

### Confusion Matrix
| Predict   |   LOCATION |      O |   PERSON |
|:----------|-----------:|-------:|---------:|
| Actual    |            |        |          |
| LOCATION  |        170 |  15766 |      183 |
| O         |       3772 | 407861 |     5332 |
| PERSON    |        131 |  17205 |      726 |

### Overall Statistics
| Name                                   | Value             |
|:---------------------------------------|:------------------|
| Overall ACC                            | 0.90604           |
| Kappa                                  | 0.02145           |
| Overall RACC                           | 0.90398           |
| Strength Of Agreement(Landis and Koch) | Slight            |
| Strength Of Agreement(Fleiss)          | Poor              |
| Strength Of Agreement(Altman)          | Poor              |
| Strength Of Agreement(Cicchetti)       | Poor              |
| TPR Macro                              | 0.34297           |
| PPV Macro                              | 0.36109           |
| TPR Micro                              | 0.90604           |
| PPV Micro                              | 0.90604           |
| Scott PI                               | 0.01064           |
| Gwet AC1                               | 0.90136           |
| Bennett S                              | 0.85906           |
| Kappa Standard Error                   | 0.00452           |
| Kappa 95% CI                           | (0.01258,0.03032) |
| Chi-Squared                            | None              |
| Phi-Squared                            | None              |
| Cramer V                               | None              |
| Chi-Squared DF                         | 4                 |
| 95% CI                                 | (0.90519,0.90689) |
| Standard Error                         | 0.00043           |
| Response Entropy                       | 0.17935           |
| Reference Entropy                      | 0.46267           |
| Cross Entropy                          | 0.52073           |
| Joint Entropy                          | None              |
| Conditional Entropy                    | None              |
| KL Divergence                          | 0.05807           |
| Lambda B                               | None              |
| Lambda A                               | None              |
| Kappa Unbiased                         | 0.01064           |
| Overall RACCU                          | 0.90503           |
| Kappa No Prevalence                    | 0.81208           |
| Mutual Information                     | None              |
| Overall J                              | (0.94577,0.31526) |

### Class Statistics
| Class   |     LOCATION |            O |       PERSON | Description                                                                                                                                                     |
|:--------|-------------:|-------------:|-------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |      0.95600 |      0.90674 |      0.94935 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |      0.00157 |      0.01357 |      0.02746 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |      1.17739 |      1.64412 |      3.24675 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |      0.04400 |      0.09326 |      0.05065 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |      0.02623 |      0.93534 |      0.08437 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |      0.01684 |      0.95095 |      0.05975 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |      0.01240 |      0.96709 |      0.04625 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |      0.95826 |      0.07479 |      0.88367 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |  15949.00000 |   9104.00000 |  17336.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |      0.98945 |      0.02183 |      0.95981 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |      0.03567 |      0.88268 |      0.03897 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   3903.00000 |  32971.00000 |   5515.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |      0.00897 |      0.96460 |      0.01273 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |      0.02098 |      0.95132 |      0.06838 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |      0.00849 |      0.90649 |      0.03079 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      1.17552 |      1.01406 |      3.15644 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |      0.99841 |      0.61678 |      0.97219 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |      0.00309 |      0.02402 |      0.04609 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |      0.00606 |      0.04252 |      0.07736 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 435027.00000 |  34181.00000 | 433084.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |      0.96433 |      0.11732 |      0.96103 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |  16119.00000 | 416965.00000 |  18062.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 451146.00000 | 451146.00000 | 451146.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |      0.04174 |      0.92521 |      0.11633 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |      0.03573 |      0.92424 |      0.04004 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |      0.00032 |      0.90311 |      0.00055 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |      0.00050 |      0.90381 |      0.00073 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 431124.00000 |   1210.00000 | 427569.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |      0.99103 |      0.03540 |      0.98727 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 447073.00000 |  10314.00000 | 444905.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   4073.00000 | 440832.00000 |   6241.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |    170.00000 | 407861.00000 |    726.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |      0.01055 |      0.97817 |      0.04019 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
