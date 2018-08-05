## StanfordNERClient
| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 97.10%     | 128953ms |         1244020 |

### Confusion Matrix
| Predict   |   LOCATION |       O |   PERSON |
|:----------|-----------:|--------:|---------:|
| Actual    |            |         |          |
| LOCATION  |      50945 |    5691 |     1733 |
| O         |      10733 | 1126143 |     4561 |
| PERSON    |        906 |   12468 |    30840 |

### Overall Statistics
| Name                                   | Value             |
|:---------------------------------------|:------------------|
| Overall ACC                            | 0.97099           |
| Kappa                                  | 0.80986           |
| Overall RACC                           | 0.84741           |
| Strength Of Agreement(Landis and Koch) | Almost Perfect    |
| Strength Of Agreement(Fleiss)          | Excellent         |
| Strength Of Agreement(Altman)          | Very Good         |
| Strength Of Agreement(Cicchetti)       | Excellent         |
| TPR Macro                              | 0.85231           |
| PPV Macro                              | 0.87622           |
| TPR Micro                              | 0.97099           |
| PPV Micro                              | 0.97099           |
| Scott PI                               | 0.80985           |
| Gwet AC1                               | 0.96859           |
| Bennett S                              | 0.95648           |
| Kappa Standard Error                   | 0.00099           |
| Kappa 95% CI                           | (0.80793,0.8118)  |
| Chi-Squared                            | None              |
| Phi-Squared                            | None              |
| Cramer V                               | None              |
| Chi-Squared DF                         | 4                 |
| 95% CI                                 | (0.97069,0.97128) |
| Standard Error                         | 0.00015           |
| Response Entropy                       | 0.47908           |
| Reference Entropy                      | 0.49212           |
| Cross Entropy                          | 0.49303           |
| Joint Entropy                          | None              |
| Conditional Entropy                    | None              |
| KL Divergence                          | 0.00091           |
| Lambda B                               | None              |
| Lambda A                               | None              |
| Kappa Unbiased                         | 0.80985           |
| Overall RACCU                          | 0.84742           |
| Kappa No Prevalence                    | 0.94198           |
| Mutual Information                     | None              |
| Overall J                              | (2.30945,0.76982) |

### Class Statistics
| Class   |      LOCATION |             O |        PERSON | Description                                                                                                                                                     |
|:--------|--------------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |       0.98468 |       0.97311 |       0.98419 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |       0.86299 |       0.80958 |       0.69227 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |     692.18227 |     342.33118 |     437.27344 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |       0.01532 |       0.02689 |       0.01581 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |       0.82514 |       0.98462 |       0.80000 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |       0.84239 |       0.98536 |       0.75822 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |       0.86038 |       0.98611 |       0.72059 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |       0.18597 |       0.01587 |       0.16949 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |    7424.00000 |   15294.00000 |   13374.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |       0.12719 |       0.01340 |       0.30248 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |       0.00628 |       0.15337 |       0.01108 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   11639.00000 |   18159.00000 |    6294.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |       0.00982 |       0.17702 |       0.00525 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |       0.84291 |       0.98537 |       0.76111 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |       0.72770 |       0.97115 |       0.61060 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      88.91203 |       5.57346 |     132.96546 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |       0.12845 |       0.01628 |       0.30408 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |       0.83491 |       0.82010 |       0.75317 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |       0.80774 |       0.83076 |       0.81942 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 1185651.00000 |  102583.00000 | 1199806.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |       0.99372 |       0.84663 |       0.98892 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |   58369.00000 | 1141437.00000 |   44214.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 1244020.00000 | 1244020.00000 | 1244020.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |       0.81403 |       0.98413 |       0.83051 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |       0.04692 |       0.91754 |       0.03554 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |       0.00236 |       0.84399 |       0.00106 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |       0.00236 |       0.84399 |       0.00107 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 1174012.00000 |   84424.00000 | 1193512.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |       0.99018 |       0.82298 |       0.99475 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 1181436.00000 |   99718.00000 | 1206886.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   62584.00000 | 1144302.00000 |   37134.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |   50945.00000 | 1126143.00000 |   30840.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |       0.87281 |       0.98660 |       0.69752 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
