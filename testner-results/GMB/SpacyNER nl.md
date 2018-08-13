## SpacyNER nl
| Accuracy   | Time     |   Total checked |
|:-----------|:---------|----------------:|
| 91.76%     | 622205ms |         1244020 |

### Confusion Matrix
| Predict   |   LOCATION |       O |   PERSON |
|:----------|-----------:|--------:|---------:|
| Actual    |            |         |          |
| LOCATION  |      27621 |   22008 |     8740 |
| O         |      24237 | 1087268 |    29932 |
| PERSON    |       2932 |   14619 |    26663 |

### Overall Statistics
| Name                                   | Value                |
|:---------------------------------------|:---------------------|
| Overall ACC                            | 0.91763              |
| Kappa                                  | 0.50715              |
| Overall RACC                           | 0.83287              |
| Strength Of Agreement(Landis and Koch) | Moderate             |
| Strength Of Agreement(Fleiss)          | Intermediate to Good |
| Strength Of Agreement(Altman)          | Moderate             |
| Strength Of Agreement(Cicchetti)       | Fair                 |
| TPR Macro                              | 0.67627              |
| PPV Macro                              | 0.62654              |
| TPR Micro                              | 0.91763              |
| PPV Micro                              | 0.91763              |
| Scott PI                               | 0.50679              |
| Gwet AC1                               | 0.91013              |
| Bennett S                              | 0.87645              |
| Kappa Standard Error                   | 0.00147              |
| Kappa 95% CI                           | (0.50426,0.51004)    |
| Chi-Squared                            | None                 |
| Phi-Squared                            | None                 |
| Cramer V                               | None                 |
| Chi-Squared DF                         | 4                    |
| 95% CI                                 | (0.91715,0.91811)    |
| Standard Error                         | 0.00025              |
| Response Entropy                       | 0.55403              |
| Reference Entropy                      | 0.49212              |
| Cross Entropy                          | 0.49688              |
| Joint Entropy                          | None                 |
| Conditional Entropy                    | None                 |
| KL Divergence                          | 0.00476              |
| Lambda B                               | None                 |
| Lambda A                               | None                 |
| Kappa Unbiased                         | 0.50679              |
| Overall RACCU                          | 0.833                |
| Kappa No Prevalence                    | 0.83526              |
| Mutual Information                     | None                 |
| Overall J                              | (1.56752,0.52251)    |

### Class Statistics
| Class   |      LOCATION |             O |        PERSON | Description                                                                                                                                                     |
|:--------|--------------:|--------------:|--------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACC     |       0.95344 |       0.92701 |       0.95481 | [Accuracy](http://www.shaghighi.ir/pycm/doc/index.html#ACC-(accuracy))                                                                                          |
| BM      |       0.45030 |       0.59550 |       0.57081 | [Informedness or bookmaker informedness](http://www.shaghighi.ir/pycm/doc/index.html#BM-(Informedness-or-Bookmaker-Informedness))                               |
| DOR     |      38.30347 |      36.14421 |      45.61344 | [Diagnostic odds ratio](http://www.shaghighi.ir/pycm/doc/index.html#DOR-(Diagnostic-odds-ratio))                                                                |
| ERR     |       0.04656 |       0.07299 |       0.04519 | [Error rate](http://www.shaghighi.ir/pycm/doc/index.html#ERR(Error-rate))                                                                                       |
| F0.5    |       0.49762 |       0.96440 |       0.43631 | [F0.5 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                           |
| F1      |       0.48818 |       0.95992 |       0.48678 | [F1 score - harmonic mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                |
| F2      |       0.47909 |       0.95548 |       0.55045 | [F2 score](http://www.shaghighi.ir/pycm/doc/index.html#FBeta-Score)                                                                                             |
| FDR     |       0.49588 |       0.03259 |       0.59190 | [False discovery rate](http://www.shaghighi.ir/pycm/doc/index.html#FDR-(false-discovery-rate))                                                                  |
| FN      |   30748.00000 |   54169.00000 |   17551.00000 | [False negative/miss/type 2 error](http://www.shaghighi.ir/pycm/doc/index.html#FN-(False-negative/miss/Type-II-error))                                          |
| FNR     |       0.52679 |       0.04746 |       0.39696 | [Miss rate or false negative rate](http://www.shaghighi.ir/pycm/doc/index.html#FNR-(miss-rate-or-false-negative-rate))                                          |
| FOR     |       0.02586 |       0.45094 |       0.01489 | [False omission rate](http://www.shaghighi.ir/pycm/doc/index.html#FOR-(false-omission-rate))                                                                    |
| FP      |   27169.00000 |   36627.00000 |   38672.00000 | [False positive/type 1 error/false alarm](http://www.shaghighi.ir/pycm/doc/index.html#FP-(False-positive/false-alarm/Type-I-error))                             |
| FPR     |       0.02291 |       0.35705 |       0.03223 | [Fall-out or false positive rate](http://www.shaghighi.ir/pycm/doc/index.html#FPR-(fall-out-or-false-positive-rate))                                            |
| G       |       0.48842 |       0.95995 |       0.49609 | [G-measure geometric mean of precision and sensitivity](http://www.shaghighi.ir/pycm/doc/index.html#G-(G-measure-geometric-mean-of-precision-and-sensitivity))  |
| J       |       0.32291 |       0.92293 |       0.32168 | [Jaccard index](http://www.shaghighi.ir/pycm/doc/#J-(Jaccard-index))                                                                                            |
| LR+     |      20.65097 |       2.66783 |      18.70956 | [Positive likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#PLR-(Positive-likelihood-ratio))                                                        |
| LR-     |       0.53914 |       0.07381 |       0.41018 | [Negative likelihood ratio](http://www.shaghighi.ir/pycm/doc/index.html#NLR-(Negative-likelihood-ratio))                                                        |
| MCC     |       0.46407 |       0.55458 |       0.47376 | [Matthews correlation coefficient](http://www.shaghighi.ir/pycm/doc/index.html#MCC-(Matthews-correlation-coefficient))                                          |
| MK      |       0.47827 |       0.51647 |       0.39321 | [Markedness](http://www.shaghighi.ir/pycm/doc/index.html#MK-(Markedness))                                                                                       |
| N       | 1185651.00000 |  102583.00000 | 1199806.00000 | [Condition negative](http://www.shaghighi.ir/pycm/doc/index.html#N-(Condition-negative))                                                                        |
| NPV     |       0.97414 |       0.54906 |       0.98511 | [Negative predictive value](http://www.shaghighi.ir/pycm/doc/index.html#NPV-(negative-predictive-value))                                                        |
| P       |   58369.00000 | 1141437.00000 |   44214.00000 | [Condition positive](http://www.shaghighi.ir/pycm/doc/index.html#P-(Condition-positive))                                                                        |
| POP     | 1244020.00000 | 1244020.00000 | 1244020.00000 | [Population](http://www.shaghighi.ir/pycm/doc/index.html#POP-(Population))                                                                                      |
| PPV     |       0.50412 |       0.96741 |       0.40810 | [Precision or positive predictive value](http://www.shaghighi.ir/pycm/doc/index.html#PPV-(precision-or-positive-predictive-value))                              |
| PRE     |       0.04692 |       0.91754 |       0.03554 | [Prevalence](http://www.shaghighi.ir/pycm/doc/index.html#PRE-(Prevalence))                                                                                      |
| RACC    |       0.00207 |       0.82894 |       0.00187 | [Random accuracy](http://www.shaghighi.ir/pycm/doc/index.html#RACC(Random-accuracy))                                                                            |
| RACCU   |       0.00207 |       0.82899 |       0.00194 | [Random accuracy unbiased](http://www.shaghighi.ir/pycm/doc/index.html#RACCU(Random-accuracy-unbiased))                                                         |
| TN      | 1158482.00000 |   65956.00000 | 1161134.00000 | [True negative/correct rejection](http://www.shaghighi.ir/pycm/doc/index.html#TN-(True-negative/correct-rejection))                                             |
| TNR     |       0.97709 |       0.64295 |       0.96777 | [Specificity or true negative rate](http://www.shaghighi.ir/pycm/doc/index.html#TNR-(specificity-or-true-negative-rate))                                        |
| TON     | 1189230.00000 |  120125.00000 | 1178685.00000 | [Test outcome negative](http://www.shaghighi.ir/pycm/doc/index.html#TON-(Test-outcome-negative))                                                                |
| TOP     |   54790.00000 | 1123895.00000 |   65335.00000 | [Test outcome positive](http://www.shaghighi.ir/pycm/doc/index.html#TOP-(Test-outcome-positive))                                                                |
| TP      |   27621.00000 | 1087268.00000 |   26663.00000 | [True positive/hit](http://www.shaghighi.ir/pycm/doc/index.html#TP-(True-positive-/-hit))                                                                       |
| TPR     |       0.47321 |       0.95254 |       0.60304 | [Sensitivity, recall, hit rate, or true positive rate](http://www.shaghighi.ir/pycm/doc/index.html#TPR--(sensitivity,-recall,-hit-rate,-or-true-positive-rate)) |
