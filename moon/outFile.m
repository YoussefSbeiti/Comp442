c	res	4
literal1	dw	14
entry
	addi r14,r0,topaddr
	lw	r1,literal1(r0)
	sw	c(r0),r1
hlt
	buf	res 20 
