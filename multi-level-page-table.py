# %%
import math

# %%
debug = False
# debug = True

page_size_B = 32
vas_size_KB = 32
pas_size_KB = 4
pte_size_B_list = [1,1]
pt_size_B_list = [32,32]
pdbr_hex = "220"
pdbr = int(pdbr_hex, 16)
num_levels = 2
if debug: print(f"pdbr: {pdbr}")

pas_filepath = "./pas.txt"

# %%
# va_hex = "6c74"
arrow = '-->'

po_bit_len = int(math.log2(page_size_B))
if debug: print(f"VPO/PPO bit length: {po_bit_len}")

vas_size_B = vas_size_KB * 1024
va_bit_len = int(math.log2(vas_size_B))
if debug: print(f"VA bit length: {va_bit_len}")
vpn_bit_len = va_bit_len - po_bit_len
if debug: print(f"VPN bit length: {vpn_bit_len}")

pas_size_B = pas_size_KB * 1024
pa_bit_len = int(math.log2(pas_size_B))
if debug: print(f"PA bit length: {pa_bit_len}")
ppn_bit_len = pa_bit_len - po_bit_len
if debug: print(f"PPN bit length: {ppn_bit_len}")

pte_size_bit_list = list(map(lambda x: x * 8, pte_size_B_list))
if debug: print(f"PTE sizes (bits): {pte_size_bit_list}")
pfn_size_bit_list = list(map(lambda x: x - 1, pte_size_bit_list))
if debug: print(f"PFN sizes (bits): {pfn_size_bit_list}")

with open(pas_filepath) as pas_file:
    lines = pas_file.readlines()
    # 用于保存解析的字节
    bytes = []

    for line in lines:
        # 如果line不为空，则处理
        if line:
            # 分割当前行，并取得16进制数值部分
            hex_values = line.split(':')[1].strip().split()

            # 将16进制的数值转为整数，并添加到列表中
            for hex_value in hex_values:
                bytes.append(int(hex_value, 16))
if debug: print(bytes)

# %%
def translate_va_hex(va_hex):
    print(f"Virtual Address: 0x{va_hex}")
    va = int(va_hex, 16)

    va_bin = f"{va:0{va_bit_len}b}"
    if debug: print(f"Virtual address: 0x{va:04x} = 0b{va_bin}", )

    po = int(va_bin[-po_bit_len:], 2)
    if debug: print(f"VPO/PPO: 0b{po:0{po_bit_len}b}")

    vpn = va_bin[:-po_bit_len]
    if debug: print(f"VPN: 0b{vpn}")

    ppn = vpn[-po_bit_len:]
    if debug: print(f"PPN: 0b{ppn}")

    if debug: print(f"PTE sizes (bits): {pte_size_bit_list}")

    # pte_size_bit_list = [1,1]
    # pt_size_B_list = [32,32]

    num_pte_list = [pt_size_B // pte_size_B for pt_size_B, pte_size_B in zip(pt_size_B_list, pte_size_B_list)]
    if debug: print(f"Number of PTEs: {num_pte_list}")
    pte_idx_bit_len_list = list(map(lambda x: int(math.log2(x)), num_pte_list))
    if debug: print(f"PTE index bit length: {pte_idx_bit_len_list}")
    assert sum(pte_idx_bit_len_list) == vpn_bit_len, "PTE index bit lengths do not add up to VPN bit length"
    pte_idxes = []
    pte_idx_start = 0
    for level, pte_idx_bit_len in enumerate(pte_idx_bit_len_list):
        if debug: print(f"PT[{level}]E index: 0b{vpn[pte_idx_start:pte_idx_start+pte_idx_bit_len]}")
        pte_idx = int(vpn[pte_idx_start:pte_idx_start+pte_idx_bit_len], 2)
        pte_idxes.append(pte_idx)
        pte_idx_start += pte_idx_bit_len

    pt_base = pdbr
    for level in range(num_levels):
        pte_idx = pte_idxes[level]
        pte_val = bytes[pt_base + pte_idx]
        pfn_size_bit = pfn_size_bit_list[level]
        if debug: print(f"PTE value: 0x{pte_val:2x} => 0b{pte_val:{pfn_size_bit}b}")
        pte_size_bit = pte_size_bit_list[level]
        pte_val_bin = f"{pte_val:0{pte_size_bit}b}"
        pte_valid_bit = int(pte_val_bin[0])
        pfn = int(pte_val_bin[1:], 2)

        if debug: print(f"PTE valid bit: {pte_valid_bit}")
        if debug: print(f"PFN: 0b{pfn:0{pfn_size_bit_list[level]}b} = 0x{pfn:02x}")

        if pte_valid_bit == 0:
            if not debug:
                print("\t"*(level + 1) + arrow + ' ' + f"pt[{level}]e index: {pte_idx} contents: (valid 0, pfn 0x{pfn:02x})")
                print("\t"*(level + 2) + arrow + ' ' + f"Fault (page table entry not valid)")
            return

        if not debug: print("\t"*(level + 1) + arrow + ' ' + f"pt[{level}]e index: {pte_idx} contents: (valid {pte_valid_bit}, pfn 0x{pfn:02x}) = 0b{pte_val_bin}")

        pt_base = pfn * pt_size_B_list[level]
        # break
    ppn = pfn
    pp_base = ppn * page_size_B
    pa = pp_base + po
    val = bytes[pa]
    print("\t"*(num_levels + 1) + arrow + ' ' + f"Translates to Physical Address: 0x{pa:04x} = 0b{pa:0{pa_bit_len}b} {arrow} Value: 0x{val:02x}")

# %%
va_hexes = [
    "6c74",
    "6b22",
    "03df",
    "69dc",
    "317a",
    "4546",
    "2c03",
    "7fd7",
    "390e",
    "748b"
]

for va_hex in va_hexes:
    translate_va_hex(va_hex)
