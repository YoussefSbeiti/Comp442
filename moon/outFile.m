a	res	4
b	res	4
c	res	4
d	res	4
e	res	4
f	res	4
literal1	dw	1
literal2	dw	2
literal3	dw	3
literal4	dw	15
literal5	dw	6
label1	res	4
label2	res	4
label3	res	4
label4	res	4
literal6	dw	42
entry
	lw	r1,literal1(r0)
	sw	a(r0),r1
	lw	r1,literal2(r0)
	sw	b(r0),r1
	lw	r1,literal3(r0)
	sw	c(r0),r1
	lw	r1,literal4(r0)
	sw	d(r0),r1
	lw	r1,literal5(r0)
	sw	e(r0),r1
	lw	r1,c(r0)
	lw	r2,d(r0)
	mul r3,r2,r1
	sw	label1(r0),r3
	lw	r1,e(r0)
	lw	r2,label1(r0)
	sub r3,r2,r1
	sw	label2(r0),r3
	lw	r1,b(r0)
	lw	r2,label2(r0)
	add r3,r2,r1
	sw	label3(r0),r3
	lw	r1,a(r0)
	lw	r2,label3(r0)
	add r3,r2,r1
	sw	label4(r0),r3
	lw	r1,label4(r0)
	sw	f(r0),r1
	lw	r1,literal6(r0)
	putc r1
hlt