# TX messages
## 2: stop (none)
## 5: connect (none)
## 6: disconnect (none)
## 9: R-test (I/10)
## 0a: Heartbeat (#) every 1m
## 01: Discharge CC (I, U/10)
## 11: Discharge CP (P, U/10)
## 21: Charge CCV (I/10, U/10, Icut)

# RX messages
## 00/0a/14: DCC idle/active/EOC
## 01/0b/15: DCP idle/active/EOC
## 02/0c/16: CCV idle/active/EOC
## 66/70:  ???? (I,U,Q) 0 (a,b,c)
   seen as 302, 2988, 2118

ccv start:
`70 00 00 10 86 00 00 00 00 01 3e 0c 6c 08 c6 09 7e`
16mA/32160mV/0mAh/1/14892/25928

oder
`70 00 00 11 0d 00 00 00 00 01 3e 0c 6c 08 c6 09 04`
17mA/3120mV/0mAh/1/14892/25928
