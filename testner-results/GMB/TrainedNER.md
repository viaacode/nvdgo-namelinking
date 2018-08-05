## TrainedNER
Tagger trained against GMB corpus.

| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 97.64%     | 821992ms |         1244020 |

### Confusion Matrix
| Predict   |   LOCATION |       O |   PERSON |
|:----------|-----------:|--------:|---------:|
| Actual    |            |         |          |
| LOCATION  |      51202 |    5937 |     1230 |
| O         |      11909 | 1122598 |     6930 |
| PERSON    |       1406 |    1973 |    40835 |

### Overall Statistics
| Name                                   | Value             |
|:---------------------------------------|:------------------|
| Overall ACC                            | 0.97638           |
| Kappa                                  | 0.85451           |
| Overall RACC                           | 0.83765           |
| Strength Of Agreement(Landis and Koch) | Almost Perfect    |
| Strength Of Agreement(Fleiss)          | Excellent         |
| Strength Of Agreement(Altman)          | Very Good         |
| Strength Of Agreement(Cicchetti)       | Excellent         |
| TPR Macro                              | 0.92809           |
| PPV Macro                              | 0.87336           |
| TPR Micro                              | 0.97638           |
| PPV Micro                              | 0.97638           |
| Scott PI                               | 0.85448           |
| Gwet AC1                               | 0.97429           |
| Bennett S                              | 0.96457           |
| Kappa Standard Error                   | 0.00084           |
| Kappa 95% CI                           | (0.85286,0.85615) |
| Chi-Squared                            | None              |
| Phi-Squared                            | None              |
| Cramer V                               | None              |
| Chi-Squared DF                         | 4                 |
| 95% CI                                 | (0.97611,0.97665) |
| Standard Error                         | 0.00014           |
| Response Entropy                       | 0.53063           |
| Reference Entropy                      | 0.49212           |
| Cross Entropy                          | 0.49281           |
| Joint Entropy                          | None              |
| Conditional Entropy                    | None              |
| KL Divergence                          | 0.00069           |
| Lambda B                               | None              |
| Lambda A                               | None              |
| Kappa Unbiased                         | 0.85448           |
| Overall RACCU                          | 0.83768           |
| Kappa No Prevalence                    | 0.95276           |
| Mutual Information                     | None              |
| Overall J                              | (2.47068,0.82356) |

### Class Statistics
| Class   |      LOCATION |             O |        PERSON | Description                                                                                                                                                     |
|:--------|--------------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |       0.98354 |       0.97850 |       0.99072 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |       0.86598 |       0.90639 |       0.91678 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |     629.01420 |     713.20778 |    1764.82428 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |       0.01646 |       0.02150 |       0.00928 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |       0.80904 |       0.99109 |       0.85004 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |       0.83333 |       0.98823 |       0.87620 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |       0.85911 |       0.98538 |       0.90403 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |       0.20638 |       0.00700 |       0.16655 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |    7167.00000 |   18839.00000 |    3379.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |       0.12279 |       0.01650 |       0.07642 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |       0.00608 |       0.16596 |       0.00283 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   13315.00000 |    7910.00000 |    8160.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |       0.01123 |       0.07711 |       0.00680 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |       0.83437 |       0.98824 |       0.87736 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |       0.71427 |       0.97673 |       0.77968 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      78.11247 |      12.75473 |     135.79808 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |       0.12418 |       0.01788 |       0.07695 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |       0.82583 |       0.86580 |       0.87264 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |       0.78754 |       0.82704 |       0.83062 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 1185651.00000 |  102583.00000 | 1199806.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |       0.99392 |       0.83404 |       0.99717 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |   58369.00000 | 1141437.00000 |   44214.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 1244020.00000 | 1244020.00000 | 1244020.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |       0.79362 |       0.99300 |       0.83345 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |       0.04692 |       0.91754 |       0.03554 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |       0.00243 |       0.83382 |       0.00140 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |       0.00244 |       0.83384 |       0.00140 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 1172336.00000 |   94673.00000 | 1191646.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |       0.98877 |       0.92289 |       0.99320 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 1179503.00000 |  113512.00000 | 1195025.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   64517.00000 | 1130508.00000 |   48995.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |   51202.00000 | 1122598.00000 |   40835.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |       0.87721 |       0.98350 |       0.92358 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
