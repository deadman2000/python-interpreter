from enum import IntFlag
from structure import DataBlock, NumberField, ByteOrder, EEnum, ArrayField, BytesField, StringField, IfField, CaseField
import datetime


# https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files
# https://msdn.microsoft.com/ru-ru/library/windows/desktop/ms680547(v=vs.85).aspx
# https://ru.wikipedia.org/wiki/Portable_Executable
# http://www.delorie.com/djgpp/doc/exe/
# http://www.tavi.co.uk/phobos/exeformat.html

# http://www.ntcore.com/files/richsign.htm


def hex_2(val):
    return '%04X' % val


class PeFormat(EEnum):
    PE32 = 0x10b
    PE64 = 0x20b
    ROM = 0x107


class MachineTypes(EEnum):
    UNKNOWN = 0x0
    AM33 = 0x1d3  # Matsushita AM33
    AMD64 = 0x8664  # x64
    ARM64 = 0xaa64  # ARM64 little endian
    ARMNT = 0x1c4  # ARM Thumb-2 little endian
    EBC = 0xebc  # EFI byte code
    I386 = 0x14c  # Intel 386 or later processors and compatible processors
    IA64 = 0x200  # Intel Itanium processor family
    M32R = 0x9041  # Mitsubishi M32R little endian
    MIPS16 = 0x266  # MIPS16
    MIPSFPU = 0x366  # MIPS with FPU
    MIPSFPU16 = 0x466  # MIPS16 with FPU
    POWERPC = 0x1f0  # Power PC little endian
    POWERPCFP = 0x1f1  # Power PC with floating point support
    R4000 = 0x166  # MIPS little endian
    RISCV32 = 0x5032  # RISC-V 32-bit address space
    RISCV64 = 0x5064  # RISC-V 64-bit address space
    RISCV128 = 0x5128  # RISC-V 128-bit address space
    SH3 = 0x1a2  # Hitachi SH3
    SH3DSP = 0x1a3  # Hitachi SH3 DSP
    SH4 = 0x1a6  # Hitachi SH4
    SH5 = 0x1a8  # Hitachi SH5
    ARM = 0x1c0  # ARM little endian
    THUMB = 0x1c2  # Thumb
    ARMV7 = 0x1c4  # ARMv7
    MIPS_R3000 = 0x162  # MIPS R3000
    MIPS_R10000 = 0x168  # MIPS R10000
    WCEMIPSV2 = 0x169  # MIPS little-endian WCE v2
    OLD_ALPHA_AXP = 0x183  # old Alpha AXP
    MOTOROLA_68000 = 0x268  # Motorola 68000 series
    ALPHA_AXP_64 = 0x284  # Alpha AXP 64-bit
    CLR_PURE_MSIL = 0xc0ee  # clr pure MSIL


class Characteristic(IntFlag):
    RELOCS_STRIPPED = 1
    EXECUTABLE_IMAGE = 2
    LINE_NUMS_STRIPPED = 4
    LOCAL_SYMS_STRIPPED = 8
    AGGRESSIVE_WS_TRIM = 0x10
    LARGE_ADDRESS_AWARE = 0x20
    BYTES_REVERSED_LO = 0x80
    I32BIT_MACHINE = 0x100
    DEBUG_STRIPPED = 0x200
    REMOVABLE_RUN_FROM_SWAP = 0x400
    NET_RUN_FROM_SWAP = 0x800
    SYSTEM = 0x1000
    DLL = 0x2000
    UP_SYSTEM_ONLY = 0x4000
    BYTES_REVERSED_HI = 0x8000


class DosHeader(DataBlock):
    fields = [
        StringField('signature', 2).must_be('MZ'),
        NumberField('bytes_in_last_block', 2),
        NumberField('blocks_in_file', 2),
        NumberField('num_relocs', 2),
        NumberField('header_paragraphs', 2),
        NumberField('min_extra_paragraphs', 2).convert(hex_2),
        NumberField('max_extra_paragraphs', 2).convert(hex_2),
        NumberField('ss', 2).convert(hex_2),
        NumberField('sp', 2).convert(hex_2),
        NumberField('checksum', 2),
        NumberField('ip', 2),
        NumberField('cs', 2),
        NumberField('reloc_table_offset', 2),
        NumberField('overlay_number', 2),
    ]


class ExeReloc(DataBlock):
    fields = [
        NumberField('offset', 2).convert(hex_2),
        NumberField('segment', 2).convert(hex_2),
    ]


class DosExtHeader(DataBlock):
    fields = [
        BytesField('reserved1', 8),
        NumberField('oem_id', 2),
        NumberField('oem_info', 2),
        BytesField('reserved2', 20),
        NumberField('e_lfanew', 4),
    ]


class PEHeader(DataBlock):
    fields = [
        StringField('signature', 4),  # Must be PE\0\0
        NumberField('machine', 2).convert(MachineTypes.from_value),
        NumberField('sections', 2),
        NumberField('datetime', 4).convert(datetime.datetime.fromtimestamp),
        NumberField('sym_tbl', 4),
        NumberField('sym_count', 4),
        NumberField('size_opt', 2),
        NumberField('characts', 2).convert(Characteristic)
    ]


class COFFHeader(DataBlock):
    fields = [
        NumberField('magic', 2).convert(PeFormat.from_value),
        NumberField('major_linker_version', 1),
        NumberField('minor_linker_version', 1),
        NumberField('size_of_code', 4),
        NumberField('size_of_init_data', 4),
        NumberField('size_of_uninit_data', 4),
        NumberField('entry_point', 4),
        NumberField('base_of_code', 4).convert(hex),
    ]


class DataDirectory(DataBlock):
    fields = [
        NumberField('addr', 4),
        NumberField('size', 4),
    ]


class PE64ExtHeader(DataBlock):
    fields = [
        NumberField('image_base', 8),
        NumberField('section_alignment', 4),
        NumberField('file_alignment', 4),
        NumberField('major_os_ver', 2),
        NumberField('minor_os_ver', 2),
        NumberField('major_image_ver', 2),
        NumberField('minor_image_ver', 2),
        NumberField('major_subs_ver', 2),
        NumberField('minor_subs_ver', 2),
        NumberField('win32_version', 4),
        NumberField('image_size', 4),
        NumberField('headers_size', 4),
        NumberField('checksum', 4),
        NumberField('subsystem', 2),
        NumberField('dll_chars', 2),
        NumberField('stacke_reserve_size', 8),
        NumberField('stacke_commit_size', 8),
        NumberField('heap_reserve_size', 8),
        NumberField('heap_commit_size', 8),
        NumberField('loader_flags', 4),
        NumberField('rva_count', 4),
        ArrayField('data_dir', DataDirectory(), lambda obj: obj.rva_count),
    ]


class PE32ExtHeader(DataBlock):
    fields = [
        NumberField('base_of_data', 4),
        NumberField('image_base', 4),
        NumberField('section_alignment', 4),
        NumberField('file_alignment', 4),
        NumberField('major_os_ver', 2),
        NumberField('minor_os_ver', 2),
        NumberField('major_subs_ver', 2),
        NumberField('minor_subs_ver', 2),
        NumberField('win32_version', 4),
        NumberField('image_size', 4),
        NumberField('headers_size', 4),
        NumberField('checksum', 4),
        NumberField('subsystem', 2),
        NumberField('dll_chars', 2),
        NumberField('stacke_reserve_size', 4),
        NumberField('stacke_commit_size', 4),
        NumberField('heap_reserve_size', 4),
        NumberField('heap_commit_size', 4),
        NumberField('loader_flags', 4),
        NumberField('rva_count', 4),
        ArrayField('data_dir', DataDirectory(), lambda obj: obj.rva_count),
    ]


class ImageSection(DataBlock):
    fields = [
        StringField('name', 8),
        NumberField('misc', 4),
        NumberField('virtual_addr', 4).convert(hex),
        NumberField('size_of_raw', 4),
        NumberField('pointer_to_raw', 4),
        NumberField('pointer_to_reloc', 4),
        NumberField('pointer_to_linenum', 4),
        NumberField('num_reloc', 2),
        NumberField('num_linemnum', 2),
        NumberField('characts', 4),
        BytesField('data', lambda obj: obj.size_of_raw)
            .set_offset(lambda obj: obj.pointer_to_raw, return_pos=True)
            .convert(lambda v: '')
    ]


class ExeFormat(DataBlock):
    byteorder = ByteOrder.BE
    fields = [
        DosHeader('dos_header'),

        DataBlock(fields=[  # Windows part
            DosExtHeader('dos_header'),
            PEHeader('pe_header').set_offset(lambda obj: obj.dos_header.e_lfanew),
            DataBlock(fields=[
                COFFHeader('coff_header'),
                CaseField('opt_header', lambda obj: obj.coff_header.magic, (
                              (PeFormat.PE32, PE32ExtHeader()),
                              (PeFormat.PE64, PE64ExtHeader())
                          ))
            ]).set_size(lambda obj: obj.pe_header.size_opt),
            ArrayField('sections', ImageSection(), lambda obj: obj.pe_header.sections),
        ]).optional(lambda obj: obj.dos_header.reloc_table_offset >= 64),

        ArrayField('relocs', ExeReloc(), lambda obj: obj.dos_header.num_relocs)
            .set_offset(lambda obj: obj.dos_header.reloc_table_offset),
    ]
