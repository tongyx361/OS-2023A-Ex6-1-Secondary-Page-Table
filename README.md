# OS-Ex6.1 二级页表

## 问题

有一台假想的计算机，页大小（page size）为 32 Bytes，支持 32KB 的虚拟地址空间（virtual address space）,有 4KB 的物理内存空间（physical memory），采用二级页表，一个页目录项（page directory entry ，PDE）大小为 1 Byte,一个页表项（page-table entries，PTEs）大小为 1 Byte，1 个页目录表大小为 32 Bytes，1 个页表大小为 32 Bytes。页目录基址寄存器（page directory base register，PDBR）保存了页目录表的物理地址（按页对齐），其值为 `0x220`（十进制为 544）。

PTE 格式（8 bit）:

```
  VALID | PFN6 ... PFN0
```

PDE 格式（8 bit）:

```
  VALID | PT6 ... PT0
```

其中

```
VALID==1表示，表示映射存在；VALID==0表示，表示映射不存在。
PFN6..0:页帧号
PT6..0:页表的物理基址>>5
```

（1）在 [物理内存模拟数据文件](https://github.com/chyyuu/os_course_exercises/blob/2018spring/all/03-2-spoc-testdata.md) 中，给出了 4KB 物理内存空间的值，请回答下列虚地址是否有合法对应的物理内存，请给出对应的 pde index, pde contents, pte index, pte contents。

```
1) Virtual Address 6c74
   Virtual Address 6b22
2) Virtual Address 03df
   Virtual Address 69dc
3) Virtual Address 317a
   Virtual Address 4546
4) Virtual Address 2c03
   Virtual Address 7fd7
5) Virtual Address 390e
   Virtual Address 748b
```

比如答案可以如下表示： (注意：下面的结果是错的，你需要关注的是如何表示)

```
Virtual Address 7570:
  --> pde index:0x1d  pde contents:(valid 1, pfn 0x33)
    --> pte index:0xb  pte contents:(valid 0, pfn 0x7f)
      --> Fault (page table entry not valid)

Virtual Address 21e1:
  --> pde index:0x8  pde contents:(valid 0, pfn 0x7f)
      --> Fault (page directory entry not valid)

Virtual Address 7268:
  --> pde index:0x1c  pde contents:(valid 1, pfn 0x5e)
    --> pte index:0x13  pte contents:(valid 1, pfn 0x65)
      --> Translates to Physical Address 0xca8 --> Value: 16
```

已有参考：[链接](https://piazza.com/class/i5j09fnsl7k5x0/post/1161) 处有参考答案。请比较你的结果与参考答案是否一致。如果不一致，请说明原因。

（2）请基于你对原理课二级页表的理解，并参考 Lab2 建页表的过程，设计一个应用程序（可基于 C、Rust、python、ruby、C++、LISP、JavaScript 等）模拟实现题目中描述的抽象 OS，正确完成二级页表转换。

已有参考：[链接](https://piazza.com/class/i5j09fnsl7k5x0/post/1161) 处有参考答案。请比较你的结果与参考答案是否一致。如果不一致，提交你的实现，并说明区别。

## 参考

- 页表详解：[9.3.2 页表  - 深入理解计算机系统（CSAPP）](https://hansimov.gitbook.io/csapp/part2/ch09-virtual-memory/9.3-vm-as-a-tool-for-caching#9.3.2-ye-biao)
- 地址翻译详解：[9.6 地址翻译 - 深入理解计算机系统（CSAPP）](https://hansimov.gitbook.io/csapp/part2/ch09-virtual-memory/9.6-address-translation)
- 已有参考：[链接](https://piazza.com/class/i5j09fnsl7k5x0/post/1161)

## 分析

默认按字节寻址
页大小（page size）为 32 Bytes —— 偏移长 5 bits
支持 32KB 的虚拟地址空间（virtual address space）——虚拟地址长 15 bits
此时可以确定：VPN 长 10 bits
有 4KB 的物理内存空间（physical memory）——物理地址长 12 bits
此时可以确定：PPN 长 8 bits
采用二级页表，
一个页目录项（page directory entry ，PDE）大小为 1 Byte——8bits
其中 7bits 为下级页表基址
1 个页目录表大小为 32 Bytes——索引对应的 VPN 片段长 5bits，与页面大小对应，与基址加起来与物理地址长相等
一个页表项（page-table entries，PTEs）大小为 1 Byte——8 bits，
其中 7bits 为 PPN
1 个页表大小为 32 Bytes——索引对应的 VPN 片段长 5bits，与基址加起来与物理地址长相等
页目录基址寄存器（page directory base register，PDBR）保存了页目录表的物理地址（按页对齐）

## （1）结果

```
Virtual Address: 0x6c74
	--> pt[0]e index: 27 contents: (valid 1, pfn 0x20) = 0b10100000
		--> pt[1]e index: 3 contents: (valid 1, pfn 0x61) = 0b11100001
			--> Translates to Physical Address: 0x0c34 = 0b110000110100 --> Value: 0x06
Virtual Address: 0x6b22
	--> pt[0]e index: 26 contents: (valid 1, pfn 0x52) = 0b11010010
		--> pt[1]e index: 25 contents: (valid 1, pfn 0x47) = 0b11000111
			--> Translates to Physical Address: 0x08e2 = 0b100011100010 --> Value: 0x1a
Virtual Address: 0x03df
	--> pt[0]e index: 0 contents: (valid 1, pfn 0x5a) = 0b11011010
		--> pt[1]e index: 30 contents: (valid 1, pfn 0x05) = 0b10000101
			--> Translates to Physical Address: 0x00bf = 0b000010111111 --> Value: 0x0f
Virtual Address: 0x69dc
	--> pt[0]e index: 26 contents: (valid 1, pfn 0x52) = 0b11010010
		--> pt[1]e index: 14 contents: (valid 0, pfn 0x7f)
			--> Fault (page table entry not valid)
Virtual Address: 0x317a
	--> pt[0]e index: 12 contents: (valid 1, pfn 0x18) = 0b10011000
		--> pt[1]e index: 11 contents: (valid 1, pfn 0x35) = 0b10110101
			--> Translates to Physical Address: 0x06ba = 0b011010111010 --> Value: 0x1e
Virtual Address: 0x4546
	--> pt[0]e index: 17 contents: (valid 1, pfn 0x21) = 0b10100001
		--> pt[1]e index: 10 contents: (valid 0, pfn 0x7f)
			--> Fault (page table entry not valid)
Virtual Address: 0x2c03
	--> pt[0]e index: 11 contents: (valid 1, pfn 0x44) = 0b11000100
		--> pt[1]e index: 0 contents: (valid 1, pfn 0x57) = 0b11010111
			--> Translates to Physical Address: 0x0ae3 = 0b101011100011 --> Value: 0x16
Virtual Address: 0x7fd7
	--> pt[0]e index: 31 contents: (valid 1, pfn 0x12) = 0b10010010
		--> pt[1]e index: 30 contents: (valid 0, pfn 0x7f)
			--> Fault (page table entry not valid)
Virtual Address: 0x390e
	--> pt[0]e index: 14 contents: (valid 0, pfn 0x7f)
		--> Fault (page table entry not valid)
Virtual Address: 0x748b
	--> pt[0]e index: 29 contents: (valid 1, pfn 0x00) = 0b10000000
		--> pt[1]e index: 4 contents: (valid 0, pfn 0x7f)
			--> Fault (page table entry not valid)
```

## （2）程序

详见 `multi-level-page-table.py` 或 `multi-level-page-table.ipynb`

直接运行即可复现结果
