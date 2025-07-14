import math

# --Editable constants--
FORMAT_THRESHOLD = 7  # the amount of e's when switching from scientific to (10^)^x format
format_decimals = 6  # amount of decimals for the "hyper-e" format, "format" and the "power10_tower" format. Keep below 16.
max_layer = 10  # amount of 10^ in power10_tower format when it switches from 10^ iterated times to 10^^x
suffix_max= 1e10 # at how much of 10^x it adds scientific notation (max is 1e308)
# --End of editable constants--

# --Editable suffix format--
FirstOnes = ["", "U", "D", "T", "Qd", "Qn", "Sx", "Sp", "Oc", "No"]
SecondOnes = ["", "De", "Vt", "Tg", "qg", "Qg", "sg", "Sg", "Og", "Ng"]
ThirdOnes = ["", "Ce", "Du", "Tr", "Qa", "Qi", "Se", "Si", "Ot", "Ni"]
MultOnes = [
    "", "Mi", "Mc", "Na", "Pi", "Fm", "At", "Zp", "Yc", "Xo", "Ve", "Me", "Due", 
    "Tre", "Te", "Pt", "He", "Hp", "Oct", "En", "Ic", "Mei", "Dui", "Tri", "Teti", 
    "Pti", "Hei", "Hp", "Oci", "Eni", "Tra", "TeC", "MTc", "DTc", "TrTc", "TeTc", 
    "PeTc", "HTc", "HpT", "OcT", "EnT", "TetC", "MTetc", "DTetc", "TrTetc", "TeTetc", 
    "PeTetc", "HTetc", "HpTetc", "OcTetc", "EnTetc", "PcT", "MPcT", "DPcT", "TPCt", 
    "TePCt", "PePCt", "HePCt", "HpPct", "OcPct", "EnPct", "HCt", "MHcT", "DHcT", 
    "THCt", "TeHCt", "PeHCt", "HeHCt", "HpHct", "OcHct", "EnHct", "HpCt", "MHpcT", 
    "DHpcT", "THpCt", "TeHpCt", "PeHpCt", "HeHpCt", "HpHpct", "OcHpct", "EnHpct", 
    "OCt", "MOcT", "DOcT", "TOCt", "TeOCt", "PeOCt", "HeOCt", "HpOct", "OcOct", 
    "EnOct", "Ent", "MEnT", "DEnT", "TEnt", "TeEnt", "PeEnt", "HeEnt", "HpEnt", 
    "OcEnt", "EnEnt", "Hect", "MeHect"
]
# --End of editable suffix format--

LARGE_HEIGHT_THRESHOLD = 9007199254740991  # 2**53-1, the largest integer that can be represented exactly in python's float
PRECISION_LIMIT = 1e-308
MIN_EXPONENT = -1e308
MAX_EXPONENT = 1e308

def get_sign_and_abs(x):
    if x is None:
        return 1, None
    if isinstance(x, (int, float)):
        if x < 0:
            return -1, -x
        else:
            return 1, x
    elif isinstance(x, str):
        if x.startswith('-'):
            return -1, x[1:]
        else:
            return 1, x
    else:
        return 1, x

def apply_sign(x, sign):
    if sign == 1:
        return x
    else:
        return negate(x)

def negate(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        if x == 0:
            return 0
        return -x
    elif isinstance(x, str):
        if x.startswith('-'):
            return x[1:]
        else:
            return '-' + x
    else:
        return '-' + str(x)

def compare_positive(a, b):
    if eq(a, b) == True:
        return 0
    elif gt(a, b) == True:
        return 1
    else:
        return -1

def tetration(a, h):
    try:
        h_float = float(h)
    except (TypeError, ValueError):
        return "Error: Tetration height must be a valid number"
    
    sign_a, abs_a = get_sign_and_abs(a)
    if sign_a == -1:
        return "Error: Tetration base must be non-negative"
    
    a_val = abs_a
    
    if h_float < 0:
        return "Error: Tetration height must be non-negative"
    
    try:
        a_float = float(a_val)
        use_float = True
    except (TypeError, ValueError):
        use_float = False
        
    if not use_float:
        if isinstance(a_val, str):
            s = slog(a_val)
            if math.isnan(s) or math.isinf(s) or s == "Error: x can't be a negative number":
                return "NaN"
            try:
                return tetration(10, float(s) + h_float - 1)
            except:
                return "NaN"
        else:
            return "NaN"
    
    a_float = float(a_val)
    if a_float < 0:
        return "Error: Tetration base must be non-negative"
    if a_float == 0:
        if h_float == 0:
            return "NaN"
        return "0" if h_float % 2 == 0 else ("1" if h_float == 1 else "0")
    if a_float == 1:
        return "1"
    
    if h_float >= LARGE_HEIGHT_THRESHOLD:
        if abs(h_float - round(h_float)) < 1e-12:
            height_str = format_int_scientific(int(round(h_float)))
        else:
            height_str = format_float_scientific(h_float)
        return f"10^^{height_str}"
    
    log10a = math.log10(a_float) if a_float > 0 else -float('inf')
    log_log10a = math.log10(log10a) if log10a > 0 else -float('inf')
    
    try:
        n = math.floor(h_float)
    except (ValueError, TypeError, OverflowError):
        return "NaN"
    
    f = h_float - n
    current = a_float ** f if f > 0 else 1.0
    layer = 0
    if n == 0:
        if current < 1e12:
            return current
        if abs(current - round(current)) < 1e-10:
            return format_float_scientific(round(current))
        return f"{current:.15g}"
    
    n_remaining = int(n)
    layer0_iter = 0
    prev_current = current
    while n_remaining > 0:
        if layer == 0:
            if layer0_iter >= 10000:
                if abs(current - prev_current) < 1e-10:
                    break
                prev_current = current
                layer0_iter = 0
            next_log10 = current * log10a
            if next_log10 > 307:
                current = next_log10
                layer = 1
            else:
                try:
                    current = a_float ** current
                except (OverflowError, ValueError):
                    current = next_log10
                    layer = 1
            layer0_iter += 1
            n_remaining -= 1
        elif layer == 1:
            current = log_log10a + current
            layer += n_remaining
            n_remaining = 0
        else:
            layer += n_remaining
            n_remaining = 0
    
    if layer >= 1 and math.isfinite(current) and current > LARGE_HEIGHT_THRESHOLD:
        while current > LARGE_HEIGHT_THRESHOLD:
            current = math.log10(current)
            layer += 1
    
    if layer == 0:
        if current < 1e12:
            return current
        if math.isnan(current):
            return "NaN"
        if abs(current - round(current)) < 1e-10:
            return format_float_scientific(round(current))
        return f"{current:.15g}"
    elif layer == 1:
        return f"e{current:.15g}"
    elif layer <= FORMAT_THRESHOLD:
        return 'e' * layer + f"{current:.15g}"
    else:
        return f"(10^)^{layer} {current:.15g}"

def slog_numeric(x, base):
    if base <= 0 or base == 1:
        return float('nan')
    sign_x, abs_x = get_sign_and_abs(x)
    if sign_x == -1:
        return float('nan')
    x = abs_x
    
    try:
        x_val = float(x)
    except (TypeError, ValueError):
        return float('nan')
    
    if x_val <= 0:
        return float('-inf')
    
    count = 0.0
    current = x_val
    while current < 1:
        if current <= 0:
            return float('-inf')
        try:
            current = base ** current
        except OverflowError:
            current = 0
        count -= 1
    while current > base:
        try:
            current = math.log(current, base)
        except (OverflowError, ValueError):
            return float('nan')
        count += 1
    
    try:
        frac = math.log(current, base)
    except (OverflowError, ValueError):
        return float('nan')
    return count + frac

def slog(x, base=10):
    sign_x, abs_x = get_sign_and_abs(x)
    if sign_x == -1:
        return "Error: x can't be a negative number"
    x = abs_x
    
    if x == 0:
        return -1
    
    if isinstance(x, str):
        if base == 10:
            if x.startswith("10^^"):
                try:
                    return float(x[4:])
                except:
                    return float('nan')
            elif x.startswith("(10^)^"):
                parts = x.split(' ', 1)
                if len(parts) < 2:
                    return float('nan')
                head, mantissa_str = parts
                k_str = head[6:]
                try:
                    k = int(k_str)
                    mantissa = float(mantissa_str)
                except:
                    return float('nan')
                return k + slog_numeric(mantissa, 10)
            else:
                count = 0
                s = x
                while s.startswith('e'):
                    count += 1
                    s = s[1:]
                if count == 0:
                    try:
                        return slog_numeric(float(x), 10)
                    except:
                        return float('nan')
                else:
                    try:
                        mantissa = float(s)
                    except:
                        return float('nan')
                    return count + slog_numeric(mantissa, 10)
        else:
            count = 0.0
            s = x
            while s:
                if s.startswith("10^^"):
                    height_str = s[4:]
                    try:
                        height = float(height_str)
                    except:
                        try:
                            return count + slog_numeric(float(s), base)
                        except:
                            return float('nan')
                    count += height
                    return count
                elif s.startswith("(10^)^"):
                    parts = s.split(' ', 1)
                    if len(parts) < 2:
                        try:
                            return count + slog_numeric(float(s), base)
                        except:
                            return float('nan')
                    head, mantissa_str = parts
                    k_str = head[6:]
                    try:
                        k = int(k_str)
                        mantissa = float(mantissa_str)
                    except:
                        return float('nan')
                    count += k
                    s = mantissa_str
                elif s.startswith('e'):
                    idx = 0
                    while idx < len(s) and s[idx] == 'e':
                        idx += 1
                    rest = s[idx:]
                    count += idx
                    s = rest
                else:
                    try:
                        return count + slog_numeric(float(s), base)
                    except:
                        return float('nan')
            return count
    else:
        return slog_numeric(x, base)

def log(x):
    sign_x, abs_x = get_sign_and_abs(x)
    if sign_x == -1:
        return "Error: Logarithm of negative number"
    x = abs_x
    
    if isinstance(x, str):
        if x == "NaN" or x.startswith("Error:"):
            return x
        if x.startswith("10^^"):
            if float(x.strip('10^^')) < LARGE_HEIGHT_THRESHOLD:
                try:
                    return correct("10^^" + str(float(x[4:]) - 1))
                except:
                    return str(x)
        elif x.startswith("(10^)^"):
            parts = x.split(' ', 1)
            if len(parts) < 2:
                return "NaN"
            head, mantissa_str = parts
            k_str = head[6:]
            try:
                k = int(k_str)
                mantissa = float(mantissa_str)
            except:
                return "NaN"
            if k == 1:
                return str(mantissa)
            if k >= LARGE_HEIGHT_THRESHOLD:
                return correct(x)
            else:
                return f"(10^)^{k-1} {mantissa_str}"
        elif x.startswith('e'):
            count = 0
            s = x
            while s.startswith('e'):
                count += 1
                s = s[1:]
            if count == 1:
                return s
            else:
                return correct('e' * (count - 1) + s)
        else:
            try:
                num_val = float(x)
                return str(math.log10(num_val))
            except:
                return "NaN"
    else:
        try:
            return math.log10(x)
        except:
            return "NaN"

def addlayer(a, b=1):
    s = slog(a)
    try:
        if math.isinf(s) or math.isnan(s) or isinstance(s, str):
            return "NaN"
    except:
        return "NaN"
    try:
        return tetration(10, float(b) + float(s))
    except (ValueError, TypeError, OverflowError):
        return "Error trying to do ``addlayer``"

def is_float_convertible(x):
    try:
        float(x)
        return True
    except:
        return False

def subtract_positive(a, b, depth=0):
    MAX_DEPTH = 3
    if depth > MAX_DEPTH:
        return a
    if a in [0, "0"]:
        return negate(b)
    if b in [0, "0"]:
        return a
    if is_float_convertible(a) and is_float_convertible(b):
        a_float = float(a)
        b_float = float(b)
        result = a_float - b_float
        if result < 0:
            return negate(str(abs(result)))
        if result == 0:
            return 0
        if abs(result) < 1e-3 or abs(result) >= 1e12:
            return format_float_scientific(result)
        return str(result)
    
    if lt(a, b) == True:
        return negate(subtract_positive(b, a, depth+1))
    
    if eq(a, b) == True:
        return 0
    
    if isinstance(a, str) and a.startswith('e') and is_float_convertible(b):
        try:
            exponent = float(a[1:])
            if exponent > 1e2:
                a_val = 10 ** exponent
                if a_val > 1e100:
                    return a
            else:
                a_val = 10 ** exponent
            result = a_val - float(b)
            if result <= 0:
                return 0
            if result < 1e12:
                return result
            return "e" + str(math.log10(result))
        except:
            pass 
    A = log(a)
    B = log(b)
    if A == "NaN" or B == "NaN" or A == "Error: Logarithm of negative number" or B == "Error: Logarithm of negative number":
        return a
    
    D = subtract_positive(A, B, depth+1)
    if D == "NaN" or D == "Error: Logarithm of negative number":
        return a
    
    try:
        D_float = float(D)
        if D_float > 1000:
            return a
        C = 10**D_float - 1
        if C <= 0:
            return 0
        log10C = math.log10(C)
        B_float = float(B)
        new_exp = B_float + log10C
        return "e" + str(new_exp)
    except:
        return a

def add_positive(a, b):
    if a in [0, "0"]:
        return b
    if b in [0, "0"]:
        return a
    if is_float_convertible(a) and is_float_convertible(b):
        a_float = float(a)
        b_float = float(b)
        result = a_float + b_float
        if abs(result) < 1e308:
            return result
        elif abs(result) >= 1e308:
            return format_float_scientific(result)
    
    s_a = slog(a)
    s_b = slog(b)
    if math.isnan(s_a) or math.isnan(s_b) or isinstance(s_a, str) or isinstance(s_b, str):
        return "NaN"
    if abs(s_a - s_b) >= 1:
        return a if s_a > s_b else b
    if s_a > 100 or s_b > 100:
        return a if s_a >= s_b else b
    if s_a < 1 and s_b < 1:
        try:
            return float(a) + float(b)
        except:
            return a if s_a >= s_b else b
    if gt(b, a) == True:
        a, b = b, a
        s_a, s_b = s_b, s_a
    
    log_a = log(a)
    log_b = log(b)
    try:
        if is_float_convertible(log_a) and is_float_convertible(log_b):
            d_val = float(log_b) - float(log_a)
        else:
            d_exp = subtract(log_b, log_a)
            d_val = float(d_exp) if is_float_convertible(d_exp) else -float('inf')
    except:
        d_val = -float('inf')
    
    if d_val < MIN_EXPONENT:
        return a
    
    try:
        x = 10.0 ** d_val
        y = math.log10(1 + x)
    except:
        return a
    
    if is_float_convertible(log_a):
        new_exponent = float(log_a) + y
    else:
        try:
            new_exponent = addition(log_a, y)
        except:
            return a
    
    return addlayer(new_exponent)

def addition(a, b):
    try:
        a_float = float(a)
        b_float = float(b)
        if abs(a_float) < 5e307 and abs(b_float) < 5e307:
            return a_float + b_float
    except (ValueError, TypeError, OverflowError):
        pass
    
    sign_a, abs_a = get_sign_and_abs(a)
    sign_b, abs_b = get_sign_and_abs(b)
    
    if abs_a in [0, "0"] and abs_b in [0, "0"]:
        return 0
    if abs_a in [0, "0"]:
        return apply_sign(abs_b, sign_b)
    if abs_b in [0, "0"]:
        return apply_sign(abs_a, sign_a)
    
    if sign_a == sign_b:
        result = add_positive(abs_a, abs_b)
        return apply_sign(result, sign_a)
    
    cmp = compare_positive(abs_a, abs_b)
    if cmp == 0:
        return 0
    elif cmp > 0:
        result = subtract_positive(abs_a, abs_b, 0)
        return apply_sign(result, sign_a)
    else:
        result = subtract_positive(abs_b, abs_a, 0)
        return apply_sign(result, sign_b)

def subtract(a, b):
    return addition(a, negate(b))

def multiply(a, b):
    sign_a, abs_a = get_sign_and_abs(a)
    sign_b, abs_b = get_sign_and_abs(b)
    sign = sign_a * sign_b
    
    if abs_a in [0, "0"] or abs_b in [0, "0"]:
        return 0

    try:
        a_float = float(abs_a)
        b_float = float(abs_b)
        product = a_float * b_float
        if not math.isinf(product) and abs(product) < 1e308:
            return apply_sign(product, sign)
    except (ValueError, TypeError, OverflowError):
        pass

    try:
        log_a = log(abs_a)
        log_b = log(abs_b)
        if log_a == "Error: Logarithm of negative number" or log_b == "Error: Logarithm of negative number":
            return "Error: Logarithm of negative number"
        
        log_product = addition(log_a, log_b)
        product = addlayer(log_product)
        return apply_sign(product, sign)
    except:
        return "Error doing multiplication"

def division(a, b):
    sign_a, abs_a = get_sign_and_abs(a)
    sign_b, abs_b = get_sign_and_abs(b)
    sign = sign_a * sign_b
    
    if abs_b in [0, "0"]:
        return "Error: Division by zero"
    if abs_a in [0, "0"]:
        return 0

    try:
        a_float = float(abs_a)
        b_float = float(abs_b)
        quotient = a_float / b_float
        if not math.isinf(quotient) and abs(quotient) < 1e308:
            return apply_sign(quotient, sign)
    except (ValueError, TypeError, OverflowError):
        pass

    try:
        log_a = log(abs_a)
        log_b = log(abs_b)
        if log_a == "Error: Logarithm of negative number" or log_b == "Error: Logarithm of negative number":
            return "Error: Logarithm of negative number"
        
        log_quotient = subtract(log_a, log_b)
        quotient = addlayer(log_quotient)
        return apply_sign(quotient, sign)
    except:
        return "Error doing division"

def power(a, b):
    sign_a, abs_a = get_sign_and_abs(a)

    if sign_a == -1:
        try:
            b_float = float(b)
            if abs(b_float - round(b_float)) < 1e-10:
                exponent_int = int(round(b_float))
                sign_result = -1 if exponent_int % 2 == 1 else 1
                abs_result = power(abs_a, b)
                return apply_sign(abs_result, sign_result)
            else:
                return "Error: Fractional exponent of negative base"
        except:
            return "Error: Invalid exponent for negative base"

    try:
        log_a = log(abs_a)
        if log_a == "Error: Logarithm of negative number":
            return "Error: Logarithm of negative number"
        
        log_power = multiply(log_a, b)
        result = addlayer(log_power)
        return result
    except:
        return "Error doing power"

def root(a, b):
    if b == 0:
        return "Error: Root of order 0"
    return power(a, division(1, b))

def sqrt(x):
    return root(x, 2)

def factorial(n):
    sign, abs_n = get_sign_and_abs(n)
    if sign == -1:
        return "Factorial can't be negative"
    
    try:
        n_val = float(abs_n)
    except (TypeError, OverflowError, ValueError):
        n_val = str(abs_n)
    
    if n_val == 0:
        return 1

    try:
        if n_val < 170:
            return math.gamma(n_val + 1)
    except (ValueError, TypeError, OverflowError):
        pass
    if gt(n_val, "e1000000000000") == True:
        return addlayer(n_val)
    else:
        term1 = multiply(addition(n_val, 0.5), log(n_val))
        term2 = negate(multiply(n_val, 0.4342944819032518))
        total_log = addition(addition(term1, term2), 0.3990899341790575)
        return addlayer(total_log)

# Comparisons
def gt(a, b):
    sign_a, abs_a = get_sign_and_abs(a)
    sign_b, abs_b = get_sign_and_abs(b)
    
    if sign_a != sign_b:
        return sign_a > sign_b
    
    if sign_a == 1:
        a_slog = slog(abs_a)
        b_slog = slog(abs_b)
        try:
            if math.isnan(a_slog) or math.isnan(b_slog) or isinstance(a_slog, str) or isinstance(b_slog, str):
                return False
        except:
            return False
        
        if a_slog > b_slog:
            return True
        elif a_slog < b_slog:
            return False
        else:
            if is_float_convertible(abs_a) and is_float_convertible(abs_b):
                return float(abs_a) > float(abs_b)
            else:
                return False
    else:
        a_slog = slog(abs_a)
        b_slog = slog(abs_b)
        if math.isnan(a_slog) or math.isnan(b_slog) or isinstance(a_slog, str) or isinstance(b_slog, str):
            return False
        if a_slog < b_slog:
            return True
        elif a_slog > b_slog:
            return False
        else:
            if is_float_convertible(abs_a) and is_float_convertible(abs_b):
                return float(abs_a) < float(abs_b)
            else:
                return False

def lt(a, b):
    return gt(b, a)

def eq(a, b):
    sign_a, abs_a = get_sign_and_abs(a)
    sign_b, abs_b = get_sign_and_abs(b)
    
    if sign_a != sign_b:
        return False
    
    try:
        a_slog = slog(abs_a)
        b_slog = slog(abs_b)
    except:
        return False
    
    try:
        if math.isnan(a_slog) or math.isnan(b_slog) or isinstance(a_slog, str) or isinstance(b_slog, str):
            return False
    except:
        return False
    
    if abs(a_slog - b_slog) > 1e-10:
        return False
    
    if is_float_convertible(abs_a) and is_float_convertible(abs_b):
        return abs(float(abs_a) - float(abs_b)) < 1e-10
    return True

def gte(a, b):
    return not lt(a, b)

def lte(a, b):
    return not gt(a, b)

# Short names
def fact(x): return factorial(x)
def pow(a, b): return power(a, b)
def tetr(a, h): return tetration(a, h)
def mul(a, b): return multiply(a, b)
def add(a, b): return addition(a, b)
def sub(a, b): return subtract(a, b)
def div(a, b): return division(a, b)

# Formats
def hyper_e(tet, decimals=format_decimals):
    if isinstance(tet, (int, float)):
        return comma_format(tet, decimals)
    tet_str = str(tet)
    if tet_str.startswith("10^^"):
        height = tet_str[4:]
        return f"E10#{height}"
    if tet_str.startswith("(10^)^"):
        parts = tet_str.split(' ', 1)
        if len(parts) == 2:
            head, mant = parts
            try:
                layers = int(head[6:])
                return f"E{mant}#{layers}"
            except ValueError:
                pass
    idx = 0
    while idx < len(tet_str) and tet_str[idx] == 'e':
        idx += 1
    if idx > 0:
        mant_str = tet_str[idx:]
        try:
            mant_val = float(mant_str)
            if idx > 1:
                return f"E{comma_format(mant_val, decimals)}#{idx}"
            else:
                return f"{comma_format(addlayer(mant_val), decimals)}"
        except ValueError:
            pass
    return tet_str

def format(tet, decimals=format_decimals):
    if isinstance(tet, (int, float)):
        return comma_format(tet, decimals)
    tet_str = tet
    if tet_str.startswith("10^^"):
        height = float(tet_str[4:])
        return f"F{comma_format(height, 6)}"
    try:
        val = float(tet_str)
        if abs(val) < 1e308:
            return comma_format(val, decimals)
    except ValueError:
        pass
    if tet_str.startswith("(10^)^"):
        parts = tet_str.split(' ', 1)
        if len(parts) == 2:
            head, mant = parts
            try:
                layers = int(head[len("(10^)^"):])
                mant_val = float(mant)
                if abs(mant_val - 1e10) < 1e-5:
                    return f"F{comma_format(layers + 2, 6)}"
                elif mant_val < 10:
                    return f"{mant_val:.{decimals}f}F{comma_format(layers, 0)}"
                elif mant_val < 1e10:
                    return f"{math.log10(mant_val):.{decimals}f}F{comma_format(layers + 1, 0)}"
                else:
                    return f"{math.log10(math.log10(mant_val)):.{decimals}f}F{comma_format(layers + 2, 0)}"
            except ValueError:
                pass
    if tet_str.startswith('e'):
        idx = 0
        while idx < len(tet_str) and tet_str[idx] == 'e':
            idx += 1
        rest = tet_str[idx:]
        exp_pos = rest.rfind('e')
        if exp_pos > 0:
            mant_str = rest[:exp_pos]
            exp_str = rest[exp_pos+1:]
            try:
                mant_f = float(mant_str)
                exp_i = int(exp_str)
                return f"{'e'*idx}{comma_format(mant_f, decimals)}e{comma_format(exp_i, 0)}"
            except ValueError:
                pass
        try:
            mant = float(rest)
            return f"{'e'*idx}{comma_format(mant, decimals)}"
        except ValueError:
            pass
    return tet_str

def power10_tower(tet, max_layers=max_layer, decimals=format_decimals):
    s = slog(tet)
    if math.isnan(s) or math.isinf(s) or isinstance(s, str):
        return "NaN"
    if s > max_layers:
        return "10^^" + comma_format(s)
    height = int(math.floor(s))
    frac = s - height
    if height <= 0:
        return frac
    mant = addlayer(frac, 2)
    expr = comma_format(float(mant), decimals)
    for _ in range(height - 1):
        expr = f"10^{expr}"
    return expr

def letter(s: str) -> str:
    s = correct(s)
    try: 
        if float(s) < 1e6: return float(s)
    except: 
        pass
    try: 
        s = format_float_scientific(s)  
    except: 
        pass
    if s.startswith("10^^") or s.startswith("(10^)^"):
        return format(s)
    if 'e' in s and not s.startswith('e') and not s.startswith("10^^") and not s.startswith("(10^)^"):
        parts = s.split('e', 1)
        if len(parts) == 2:
            try:
                mantissa = float(parts[0])
                exponent = float(parts[1])
                if exponent.is_integer():
                    exponent_int = int(exponent)
                    leftover = exponent_int % 3
                    group = exponent_int // 3 - 1
                    new_mantissa = mantissa * (10 ** leftover)
                    if abs(new_mantissa - round(new_mantissa)) < 1e-5:
                        formatted = str(int(round(new_mantissa)))
                    else:
                        formatted = f"{new_mantissa:.2f}".rstrip('0').rstrip('.')
                    if group < 0:
                        value = mantissa * (10 ** exponent_int)
                        return str(int(value)) if value.is_integer() else f"{value:.2f}"
                    elif group == 0:
                        return formatted
                    elif group == 1:
                        return formatted + "M"
                    elif group == 2:
                        return formatted + "B"
                    else:
                        suffix = get_short_scale_suffix(group)
                        return formatted + suffix
            except (ValueError, OverflowError): 
                pass
    k = 0
    while k < len(s) and s[k] == 'e':
        k += 1
    rest = s[k:]
    
    if k == 0: 
        return s
    try:
        exponent_val = float(rest)
        if exponent_val < 0: return "0"
    except (ValueError, OverflowError): 
        return s
    if exponent_val > suffix_max:
        if abs(exponent_val - round(exponent_val)) < 1e-5:
            exponent_str = str(int(round(exponent_val)))
        else:
            exponent_str = str(exponent_val)
        return 'e(' + letter(format_float_scientific(exponent_str)) + ')'
    if k == 1:
        try:
            leftover = exponent_val % 3
            group = exponent_val // 3 - 1
            if group < 0:
                value = 10 ** exponent_val
                return str(int(value)) if value.is_integer() else f"{value:.2f}"
            mantissa_val = 10 ** leftover
            if mantissa_val >= 999.995:
                mantissa_val /= 1000.0
                group += 1
            if abs(mantissa_val - round(mantissa_val)) < 1e-5:
                formatted = str(int(round(mantissa_val)))
            else:
                formatted = f"{mantissa_val:.2f}".rstrip('0').rstrip('.')

            if group == 0:
                return formatted
            elif group == 1:
                return formatted + "M"
            elif group == 2:
                return formatted + "B"
            else:
                suffix = get_short_scale_suffix(int(group))
                return formatted + suffix
        except (ValueError, OverflowError):
            return s
    if k == 2:
        try:
            exponent_val = float(rest)
            if not exponent_val.is_integer():
                exponent_val = round(exponent_val)
            exponent_val = int(exponent_val)
            if suffix_max > 0:
                threshold = math.ceil(math.log10(suffix_max + 1))
            else:
                threshold = 0

            if exponent_val >= threshold:
                return 'e(' + letter("e" + rest) + ')'
            else:
                power_val = 10 ** exponent_val
                group_index = (power_val - 3) // 3
                suffix = get_short_scale_suffix(int(group_index))
                return "10" + suffix
        except (ValueError, OverflowError):
            return 'e(' + letter("e" + rest) + ')'

    return fix_letter_output((k-2)*'e' + '(' + letter("ee" + rest) + ')')
# Helper formats
def comma_format(number, decimals=format_decimals):
    try:
        num_float = float(number)
        if abs(num_float) < 1e-3 or abs(num_float) >= 1e12:
            s = f"{num_float:.{decimals}e}"
            if 'e' in s:
                mant, exp = s.split('e')
                exp = exp.lstrip('+').lstrip('0') or '0'
                return f"{mant}e{exp}"
            return s
        return f"{num_float:,.{decimals}f}"
    except:
        return str(number)

def format_int_scientific(n: int, sig_digits: int = 16) -> str:
    s = f"{n:.{sig_digits}e}"
    mant, exp = s.split('e')
    mant = mant.rstrip('0').rstrip('.')
    exp = exp.lstrip('+').lstrip('0') or '0'
    return f"{mant}e{exp}"

def format_float_scientific(x: float, sig_digits: int = 16) -> str:
    if float(x) <= 0 or math.isinf(float(x)) or math.isnan(float(x)):
        return str(x)
    exp = math.floor(math.log10(abs(float(x))))
    mant = float(x) / (10 ** exp)
    mant_str = f"{mant:.{sig_digits}g}".rstrip('0').rstrip('.')
    return f"{mant_str}e{exp}"

def correct(x):
    return tetr(10, slog(x))

def fix_letter_output(s):
    cleaned = ''.join(c for c in s if c not in '()')
    e_count = 0
    i = 0
    while i < len(cleaned) and cleaned[i] == 'e':
        e_count += 1
        i += 1
    if i < len(cleaned) and cleaned[i].isdigit():
        prefix = 'e' * e_count
        suffix = cleaned[i:]
        return f"{prefix}({suffix})"
    else:
        return "Error: error formatting the short format value"

def get_short_scale_suffix(n: int) -> str:
    if n == 0:
        return ""
    if n < 1000:
        hundreds = n // 100
        tens = (n % 100) // 10
        units = n % 10
        return FirstOnes[units] + SecondOnes[tens] + ThirdOnes[hundreds]
    
    for i in range(len(MultOnes)-1, 0, -1):
        magnitude = 1000 ** i
        if n < magnitude:
            continue
        count = n // magnitude
        remainder = n % magnitude
        if count == 1:
            count_str = ""
        else:
            count_str = get_short_scale_suffix(count)
            
        rem_str = get_short_scale_suffix(remainder) if remainder > 0 else ""
        return count_str + MultOnes[i] + rem_str
    
    return ""
