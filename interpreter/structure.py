import io
from enum import Enum, IntEnum
from typing import List


class EEnum(IntEnum):
    @classmethod
    def find_value(cls, value):
        return any(value == item.value for item in cls)

    @classmethod
    def from_value(cls, value):
        if cls.find_value(value):
            return cls(value)
        return value


class ByteOrder(Enum):
    BE = 0,
    LE = 1


class StreamWrapper:
    def __init__(self, stream: io.BytesIO, offset=0):
        self.stream = stream
        self.offset = offset  # Offset in global stream

    def read(self, *args, **kwargs):
        return self.stream.read(*args, **kwargs)

    def seek(self, pos):
        return self.stream.seek(pos - self.offset)

    def tell(self):
        return self.offset + self.stream.tell()


class AttrDict(dict):
    def __init__(self, parent=None):
        super(AttrDict, self).__init__()
        self.__dict__ = self
        self.__parent__ = parent


def get_value(value, obj):
    if hasattr(value, '__call__'):  # it's lambda or method
        return value(obj)
    return value


def clean_obj(obj):
    if isinstance(obj, AttrDict):
        obj.pop('__parent__', None)
        for key, val in obj.items():
            clean_obj(val)
    elif isinstance(obj, list):
        for val in obj:
            clean_obj(val)


def reorganize_meta(obj):
    result = {}
    for key, val in obj.items():
        if key.startswith('$'):
            continue

        m = obj['$' + key]
        if m['size'] <= 0:
            assert (m['size'] == 0)
            continue

        if isinstance(val, dict):
            val = reorganize_meta(val)
        elif isinstance(val, list):
            arr_dict = {}
            for i in range(len(val)):
                elmeta = obj['$' + key + '[' + str(i) + ']']
                elval = val[i]
                if isinstance(elval, dict):
                    elval = reorganize_meta(elval)

                arr_dict[key + '[' + str(i) + ']'] = {
                    **elmeta,
                    'value': elval
                }
            val = arr_dict

        m['value'] = val

        result[key] = m

    return result


def reorganize_meta_compact(obj):
    result = {}
    for key, val in obj.items():
        if key.startswith('$'):
            continue

        m = obj['$' + key]
        if m['size'] <= 0:
            assert (m['size'] == 0)
            continue

        if isinstance(val, dict):
            val = reorganize_meta_compact(val)
        elif isinstance(val, list):
            arr_dict = {}
            for i in range(len(val)):
                elmeta = obj['$' + key + '[' + str(i) + ']']
                elval = val[i]
                if isinstance(elval, dict):
                    elval = reorganize_meta_compact(elval)

                arr_dict[key + '[' + str(i) + ']'] = [
                    elmeta['offset'],
                    elmeta['size'],
                    0,
                    elval
                ]
            val = arr_dict

        result[key] = [
            m['offset'],
            m['size'],
            0,
            val
        ]

    return result


class ValidationError(Exception):
    pass


class FormatError(Exception):
    pass


class Element(object):
    byteorder = None
    size = None
    offset = None
    return_pos = None
    func_opt = None
    converters = None
    with_meta = None

    def __init__(self, name=None):
        self.name = name
        self.parent = None
        self.display_name = None
        self.validator = None

    def read_value(self, stream, obj):
        # Считывает поток в объект obj
        raise NotImplementedError()

    # Parsing

    def read_stream(self, stream, obj=None, parent=None):
        if self.func_opt is not None:
            if not get_value(self.func_opt, obj):
                return obj

        if obj is None:
            obj = AttrDict(parent)

        if self.return_pos:
            old_pos = stream.tell()

        if self.offset is not None:
            offset = get_value(self.offset, obj)
            stream.seek(offset)

        pos = stream.tell()

        if self.size is not None:
            size = get_value(self.size, obj)
            data = stream.read(size)
            stream = StreamWrapper(io.BytesIO(data), pos)

        val = self.read_value(stream, obj)

        size = stream.tell() - pos

        if self.return_pos:
            stream.seek(old_pos)

        if self.converters is not None:
            for c in self.converters:
                try:
                    val = c(val)
                except Exception:
                    pass

        if self.validator:
            if not self.validator(val, obj):
                raise ValidationError()

        if self.name:  # If name is set, this element must be field id obj, else is parsed into obj
            obj[self.name] = val
            if self.is_write_meta():
                exval = obj.get('$' + self.name)
                if exval is not None:
                    pos = exval['offset']
                    size += exval['size']

                meta = {'offset': pos, 'size': size}
                self.write_metainfo(meta, val)
                obj['$' + self.name] = meta
            return obj
        else:
            return val

    def parse_stream(self, stream, to_meta=False, compact_meta=False):
        self.with_meta = to_meta
        obj = self.read_stream(StreamWrapper(stream))
        clean_obj(obj)
        if to_meta:
            if compact_meta:
                return reorganize_meta_compact(obj)
            return reorganize_meta(obj)
        return obj

    def parse_file(self, path, **kwargs):
        with open(path, "rb") as file:
            return self.parse_stream(file, **kwargs)

    def parse_bytes(self, data, **kwargs):
        return self.parse_stream(io.BytesIO(data), **kwargs)

    # Configs

    def set_parent(self, parent):
        self.parent = parent

    def is_bigendian(self):
        if self.byteorder is None and self.parent is not None:
            return self.parent.is_bigendian()
        return self.byteorder == ByteOrder.BE

    # Chaining

    def convert(self, func):
        if self.converters is None:
            self.converters = []
        self.converters.append(func)
        return self

    def set_offset(self, func_val, return_pos=False):  # TODO Relative current pos. offset
        self.offset = func_val
        self.return_pos = return_pos
        return self

    def optional(self, func_opt):
        self.func_opt = func_opt
        return self

    def set_size(self, size):
        self.size = size
        return self

    def display(self, name):
        self.display_name = name
        return self

    def set_bigendian(self):
        self.byteorder = ByteOrder.BE
        return self

    def validation(self, func):
        self.validator = func
        return self

    def must_be(self, value):
        self.validator = lambda v, o: v == value
        return self

    # Metainfo

    def write_metainfo(self, meta, obj):
        pass

    def is_write_meta(self):
        if self.with_meta is None and self.parent is not None:
            return self.parent.is_write_meta()
        return self.with_meta


class NumberField(Element):
    bytes_count = 0
    signed = False

    def __init__(self, name=None, bytes_count=0, signed=None):
        super().__init__(name)
        if bytes_count:
            self.bytes_count = bytes_count
        if signed is not None:
            self.signed = signed

    def read_value(self, stream, obj):
        if self.bytes_count == 0:
            return None

        data = stream.read(self.bytes_count)
        if len(data) < self.bytes_count:
            raise EOFError()

        val = 0
        if self.is_bigendian():  # TODO Signed support
            for i in range(len(data)):
                val |= data[i] << (i << 3)
        else:
            for b in data:
                val = b | (val << 8)

        return val

    def write_metainfo(self, meta, obj):
        meta['type'] = self.bytes_count


class ObjectElement(Element):
    def read_value(self, stream, obj):
        assert(obj is not None)
        if self.name:  # If name is set, this block must be field id obj, else is parsed into obj
            if hasattr(obj, self.name):  # Field already exists. exetend it!
                obj = obj[self.name]
            else:
                d = AttrDict(obj)
                obj[self.name] = d
                obj = d
        self.read_fields(stream, obj)
        return obj

    def read_fields(self, stream, obj):
        raise NotImplementedError()


class BitField(Element):
    def __init__(self, name, size):
        super().__init__(name)
        self.size = size

    def read_value(self, stream, obj):
        raise Exception('Field must be in BitParser')


def _read_bits_be(data, s, ind, shift):
    v = 0
    while s > 0:
        b = data[ind] >> shift
        r = 8 - shift  # Bit remains

        if s > r:
            v = v << r
            v |= b
            s -= r
            ind += 1
            shift = 0
        else:
            v = v << s
            v |= b & (0xff >> (8 - s))
            shift += s
            s = 0
    return v, ind, shift


def _read_bits_le(data, s, ind, shift):
    v = 0
    while s > 0:
        if ind >= len(data):
            raise Exception()
        b = data[ind] & (0xff >> shift)
        r = 8 - shift  # Bit remains

        if s >= r:
            v = v << r
            v |= b
            s -= r
            ind += 1
            shift = 0
        else:
            v = v << s
            v |= b >> (8 - s - shift)
            shift += s
            s = 0
    return v, ind, shift


class BitParser(ObjectElement):
    fields = None

    def __init__(self, name=None, fields: List[BitField] = None, bitorder: ByteOrder = ByteOrder.BE):
        super().__init__(name)
        if fields:
            self.fields = fields
        self.bitorder = bitorder

        bitcount = 0
        for f in self.fields:
            bitcount += f.size
        self.bytes_count = bitcount // 8
        if bitcount % 8 > 0:
            self.bytes_count += 1

    def read_fields(self, stream, obj):
        data = stream.read(self.bytes_count)
        ind = 0  # Current position in data
        shift = 0  # Bit shift in current position

        if self.is_bigendian():
            func = _read_bits_be
        else:
            func = _read_bits_le

        for f in self.fields:
            v, ind, shift = func(data, f.size, ind, shift)
            obj[f.name] = v


class ArrayField(Element):
    def __init__(self, name, element, count=None):
        super().__init__(name)
        self.element = element
        self.count = count
        self.element.set_parent(self)
        assert (self.element.name is None)

    def read_value(self, stream, obj):
        if self.is_write_meta():
            return self._read_value_meta(stream, obj)

        arr = []
        count = get_value(self.count, obj)
        if count is not None:
            for i in range(count):
                obj['__curr_ind__'] = i
                e = self.element.read_stream(stream, None, obj)
                arr.append(e)
        else:
            i = 0
            while True:
                obj['__curr_ind__'] = i
                try:  # TODO: Best implementation w/o exceptions
                    e = self.element.read_stream(stream, None, obj)
                    arr.append(e)
                    i += 1
                except EOFError:
                    break

        obj.pop('__curr_ind__', None)
        return arr

    def _read_value_meta(self, stream, obj):
        count = get_value(self.count, obj)
        i = 0

        arr = []
        if count is not None:
            for i in range(count):
                obj['__curr_ind__'] = i
                elname = self.name + '[' + str(i) + ']'
                e, pos, size = self._read_element_meta(stream, obj)
                arr.append(e)
                obj['$' + elname] = {'offset': pos, 'size': size}
        else:
            try:  # TODO: Best implementation w/o exceptions
                while True:
                    obj['__curr_ind__'] = i
                    elname = self.name + '[' + str(i) + ']'
                    e, pos, size = self._read_element_meta(stream, obj)
                    arr.append(e)
                    obj['$' + elname] = {'offset': pos, 'size': size}
                    i += 1
            except EOFError:
                pass

        obj.pop('__curr_ind__', None)
        return arr

    def _read_element_meta(self, stream, obj):
        pos = stream.tell()
        e = self.element.read_stream(stream, None, obj)
        size = stream.tell() - pos
        return e, pos, size


class BytesField(Element):
    def __init__(self, name=None, count=None):
        super().__init__(name)
        self.count = count

    def read_value(self, stream, obj):
        if self.count:
            return stream.read(get_value(self.count, obj))
        return stream.read()


class StringField(BytesField):
    encoding = None

    def read_value(self, stream, obj):
        val = super().read_value(stream, obj)
        if not self.encoding:
            return val.decode()
        return val.decode(self.encoding)


class DataBlock(ObjectElement):
    fields = None

    def __init__(self, name=None, fields=None, byteorder=None):
        super().__init__(name)
        if fields:
            self.fields = fields

        for f in self.fields:
            f.set_parent(self)

        if byteorder is not None:
            self.byteorder = byteorder

    def read_fields(self, stream, obj):
        for e in self.fields:
            e.read_stream(stream, obj)


class MultipleField(Element):
    def _assign_child(self, el):
        if el.name is None:
            if self.name:
                el.name = self.name
            else:
                raise FormatError('Parent or child must have name')
        el.parent = self

    def read_stream(self, stream, obj=None, parent=None):
        raise NotImplementedError()

    def read_value(self, stream, obj):
        pass


class IfField(MultipleField):
    def __init__(self, name=None, selector=None):
        super().__init__(name)
        self.selector = selector
        for expr, el in self.selector:
            self._assign_child(el)

    def read_stream(self, stream, obj=None, parent=None):
        for expr, el in self.selector:
            if get_value(expr, obj):
                return el.read_stream(stream, obj, parent)
        return obj


class CaseField(MultipleField):
    def __init__(self, name=None, expr=None, selector=None, default=None):
        super().__init__(name)
        self.expression = expr
        self.selector = selector
        self.default = default
        for val, el in self.selector:
            self._assign_child(el)
        if default:
            self._assign_child(default)

    def read_stream(self, stream, obj=None, parent=None):
        v = get_value(self.expression, obj)
        for val, el in self.selector:
            if val == v:
                return el.read_stream(stream, obj)
        if self.default:
            return self.default.read_stream(stream, obj, parent)
        return obj
