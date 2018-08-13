## SpacyNER xx
| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 96.41%     | 222213ms |         1244020 |

### Confusion Matrix
| Predict   |   LOCATION |       O |   PERSON |
|:----------|-----------:|--------:|---------:|
| Actual    |            |         |          |
| LOCATION  |      48965 |    7178 |     2226 |
| O         |      14609 | 1118126 |     8702 |
| PERSON    |       1385 |   10581 |    32248 |

### Overall Statistics
| Name                                   | Value             |
|:---------------------------------------|:------------------|
| Overall ACC                            | 0.96408           |
| Kappa                                  | 0.77344           |
| Overall RACC                           | 0.84147           |
| Strength Of Agreement(Landis and Koch) | Substantial       |
| Strength Of Agreement(Fleiss)          | Excellent         |
| Strength Of Agreement(Altman)          | Good              |
| Strength Of Agreement(Cicchetti)       | Excellent         |
| TPR Macro                              | 0.84928           |
| PPV Macro                              | 0.82835           |
| TPR Micro                              | 0.96408           |
| PPV Micro                              | 0.96408           |
| Scott PI                               | 0.77343           |
| Gwet AC1                               | 0.96099           |
| Bennett S                              | 0.94613           |
| Kappa Standard Error                   | 0.00105           |
| Kappa 95% CI                           | (0.77138,0.77551) |
| Chi-Squared                            | None              |
| Phi-Squared                            | None              |
| Cramer V                               | None              |
| Chi-Squared DF                         | 4                 |
| 95% CI                                 | (0.96376,0.96441) |
| Standard Error                         | 0.00017           |
| Response Entropy                       | 0.51048           |
| Reference Entropy                      | 0.49212           |
| Cross Entropy                          | 0.49255           |
| Joint Entropy                          | None              |
| Conditional Entropy                    | None              |
| KL Divergence                          | 0.00043           |
| Lambda B                               | None              |
| Lambda A                               | None              |
| Kappa Unbiased                         | 0.77343           |
| Overall RACCU                          | 0.84148           |
| Kappa No Prevalence                    | 0.92817           |
| Mutual Information                     | None              |
| Overall J                              | (2.20785,0.73595) |

### Class Statistics
| Class   |      LOCATION |             O |        PERSON | Description                                                                                                                                                     |
|:--------|--------------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |       0.97958 |       0.96699 |       0.98160 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |       0.82540 |       0.80646 |       0.72025 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |     380.78039 |     229.10263 |     293.19084 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |       0.02042 |       0.03301 |       0.01840 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |       0.76939 |       0.98340 |       0.74332 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |       0.79406 |       0.98197 |       0.73802 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |       0.82036 |       0.98053 |       0.73280 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |       0.24622 |       0.01563 |       0.25310 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |    9404.00000 |   23311.00000 |   11966.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |       0.16111 |       0.02042 |       0.27064 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |       0.00798 |       0.21557 |       0.00996 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   15994.00000 |   17759.00000 |   10928.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |       0.01349 |       0.17312 |       0.00911 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |       0.79520 |       0.98197 |       0.73808 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |       0.65846 |       0.96457 |       0.58482 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      62.18753 |       5.65843 |      80.07802 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |       0.16332 |       0.02470 |       0.27313 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |       0.78459 |       0.78740 |       0.72854 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |       0.74581 |       0.76879 |       0.73693 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 1185651.00000 |  102583.00000 | 1199806.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |       0.99202 |       0.78443 |       0.99004 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |   58369.00000 | 1141437.00000 |   44214.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 1244020.00000 | 1244020.00000 | 1244020.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |       0.75378 |       0.98437 |       0.74690 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |       0.04692 |       0.91754 |       0.03554 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |       0.00245 |       0.83778 |       0.00123 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |       0.00246 |       0.83779 |       0.00123 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 1169657.00000 |   84824.00000 | 1188878.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |       0.98651 |       0.82688 |       0.99089 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 1179061.00000 |  108135.00000 | 1200844.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   64959.00000 | 1135885.00000 |   43176.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |   48965.00000 | 1118126.00000 |   32248.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |       0.83889 |       0.97958 |       0.72936 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
