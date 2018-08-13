## SpacyNER en
| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 93.79%     | 588929ms |         1244020 |

### Confusion Matrix
| Predict   |   LOCATION |       O |   PERSON |
|:----------|-----------:|--------:|---------:|
| Actual    |            |         |          |
| LOCATION  |       3965 |   51969 |     2435 |
| O         |       1659 | 1134198 |     5580 |
| PERSON    |         82 |   15571 |    28561 |

### Overall Statistics
| Name                                   | Value                |
|:---------------------------------------|:---------------------|
| Overall ACC                            | 0.93787              |
| Kappa                                  | 0.44714              |
| Overall RACC                           | 0.88761              |
| Strength Of Agreement(Landis and Koch) | Moderate             |
| Strength Of Agreement(Fleiss)          | Intermediate to Good |
| Strength Of Agreement(Altman)          | Moderate             |
| Strength Of Agreement(Cicchetti)       | Fair                 |
| TPR Macro                              | 0.56919              |
| PPV Macro                              | 0.80652              |
| TPR Micro                              | 0.93787              |
| PPV Micro                              | 0.93787              |
| Scott PI                               | 0.44195              |
| Gwet AC1                               | 0.9342               |
| Bennett S                              | 0.9068               |
| Kappa Standard Error                   | 0.00193              |
| Kappa 95% CI                           | (0.44336,0.45091)    |
| Chi-Squared                            | None                 |
| Phi-Squared                            | None                 |
| Cramer V                               | None                 |
| Chi-Squared DF                         | 4                    |
| 95% CI                                 | (0.93744,0.93829)    |
| Standard Error                         | 0.00022              |
| Response Entropy                       | 0.23342              |
| Reference Entropy                      | 0.49212              |
| Cross Entropy                          | 0.59109              |
| Joint Entropy                          | None                 |
| Conditional Entropy                    | None                 |
| KL Divergence                          | 0.09898              |
| Lambda B                               | None                 |
| Lambda A                               | None                 |
| Kappa Unbiased                         | 0.44195              |
| Overall RACCU                          | 0.88866              |
| Kappa No Prevalence                    | 0.87573              |
| Mutual Information                     | None                 |
| Overall J                              | (1.55095,0.51698)    |

### Class Statistics
| Class   |      LOCATION |             O |        PERSON | Description                                                                                                                                                     |
|:--------|--------------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |       0.95487 |       0.93989 |       0.98097 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |       0.06646 |       0.33526 |       0.63929 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |      49.56011 |      81.29251 |     271.31412 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |       0.04513 |       0.06011 |       0.01903 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |       0.24417 |       0.95337 |       0.74956 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |       0.12376 |       0.96809 |       0.70704 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |       0.08289 |       0.98327 |       0.66909 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |       0.30512 |       0.05620 |       0.21913 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |   54404.00000 |    7239.00000 |   15653.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |       0.93207 |       0.00634 |       0.35403 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |       0.04393 |       0.17121 |       0.01296 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |    1741.00000 |   67540.00000 |    8015.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |       0.00147 |       0.65839 |       0.00668 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |       0.21726 |       0.96841 |       0.71022 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |       0.06596 |       0.93815 |       0.54684 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      46.26143 |       1.50922 |      96.69880 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |       0.93344 |       0.01857 |       0.35641 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |       0.20800 |       0.50894 |       0.70065 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |       0.65095 |       0.77259 |       0.76790 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 1185651.00000 |  102583.00000 | 1199806.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |       0.95607 |       0.82879 |       0.98704 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |   58369.00000 | 1141437.00000 |   44214.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 1244020.00000 | 1244020.00000 | 1244020.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |       0.69488 |       0.94380 |       0.78087 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |       0.04692 |       0.91754 |       0.03554 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |       0.00022 |       0.88635 |       0.00104 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |       0.00066 |       0.88694 |       0.00105 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 1183910.00000 |   35043.00000 | 1191791.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |       0.99853 |       0.34161 |       0.99332 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 1238314.00000 |   42282.00000 | 1207444.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |    5706.00000 | 1201738.00000 |   36576.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |    3965.00000 | 1134198.00000 |   28561.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |       0.06793 |       0.99366 |       0.64597 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
