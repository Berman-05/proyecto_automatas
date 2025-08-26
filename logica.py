from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Union, Set
import re


@dataclass(frozen=True)
class Const:
    value: bool

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Not:
    child: "Node"

@dataclass(frozen=True)
class And:
    children: Tuple["Node", ...]

@dataclass(frozen=True)
class Or:
    children: Tuple["Node", ...]

Node = Union[Const, Var, Not, And, Or]



def node_to_str(n: Node) -> str:
    if isinstance(n, Const):
        return "1" if n.value else "0"
    if isinstance(n, Var):
        return n.name
    if isinstance(n, Not):
        child = n.child

        if isinstance(child, (And, Or)):
            return f"!({node_to_str(child)})"
        return f"!{node_to_str(child)}"
    if isinstance(n, And):
        return " & ".join(_maybe_paren_for_and(c) for c in n.children)
    if isinstance(n, Or):
        return " | ".join(_maybe_paren_for_or(c) for c in n.children)
    raise TypeError("Unknown node type")

def _maybe_paren_for_and(n: Node) -> str:
    if isinstance(n, Or):
        return f"({node_to_str(n)})"
    return node_to_str(n)

def _maybe_paren_for_or(n: Node) -> str:
    if isinstance(n, And):
        return f"({node_to_str(n)})"
    return node_to_str(n)



_SYMBOL_MAP = {
    '∧': '&', '•': '&', '*': '&', '⋅': '&', 'AND': '&', 'and': '&',
    '∨': '|', '+': '|', 'OR': '|', 'or': '|',
    '¬': '!', '~': '!', 'NOT': '!', 'not': '!',
}

_ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_!&|() 01")

_var_token_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def normalize_symbols(s: str) -> str:

    for k, v in sorted(_SYMBOL_MAP.items(), key=lambda kv: -len(kv[0])):
        s = s.replace(k, v)

    s = re.sub(r"\s+", " ", s).strip()

    bad = [ch for ch in s if ch not in _ALLOWED]
    if bad:
        raise ValueError(f"Símbolos inválidos encontrados: {sorted(set(bad))}")
    return s


def parse_expression(s: str) -> Node:
    s = s.strip()
    if not s:
        raise ValueError("Expresión vacía")

    tokens = _tokenize(s)
    output: List[Node] = []
    ops: List[str] = []

    def apply_op(op: str):
        if op == '!':
            if not output:
                raise ValueError("Negación sin operando")
            a = output.pop()
            output.append(Not(a))
        elif op in ('&', '|'):
            if len(output) < 2:
                raise ValueError("Operador binario sin suficientes operandos")
            b = output.pop()
            a = output.pop()
            if op == '&':
                output.append(And((a, b)))
            else:
                output.append(Or((a, b)))
        else:
            raise ValueError(f"Operador desconocido: {op}")

    prec = {'!': 3, '&': 2, '|': 1}

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == '1':
            output.append(Const(True))
        elif t == '0':
            output.append(Const(False))
        elif _var_token_re.fullmatch(t):
            output.append(Var(t))
        elif t in ('!', '&', '|'):
            if t == '!':
                ops.append(t)
            else:
                while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[t]:
                    apply_op(ops.pop())
                ops.append(t)
        elif t == '(':
            ops.append(t)
        elif t == ')':
            while ops and ops[-1] != '(':
                apply_op(ops.pop())
            if not ops:
                raise ValueError("Paréntesis desbalanceados")
            ops.pop()
        else:
            raise ValueError(f"Token inesperado: {t}")
        i += 1

    while ops:
        op = ops.pop()
        if op in ('(', ')'):
            raise ValueError("Paréntesis desbalanceados al final")
        apply_op(op)

    if len(output) != 1:
        raise ValueError("Expresión mal formada")

    return _normalize_tree(output[0])


def _tokenize(s: str) -> List[str]:
    tokens: List[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch in '!&|()':
            tokens.append(ch)
            i += 1
            continue
        if ch.isdigit():
            tokens.append(ch)
            i += 1
            continue
        if ch.isalpha() or ch == '_':
            j = i + 1
            while j < len(s) and (s[j].isalnum() or s[j] == '_'):
                j += 1
            tokens.append(s[i:j])
            i = j
            continue
        raise ValueError(f"Carácter inválido: {ch}")
    return tokens


def _normalize_tree(n: Node) -> Node:

    if isinstance(n, (Const, Var)):
        return n
    if isinstance(n, Not):
        return Not(_normalize_tree(n.child))
    if isinstance(n, And):
        kids = []
        for c in n.children:
            c = _normalize_tree(c)
            if isinstance(c, And):
                kids.extend(c.children)
            else:
                kids.append(c)

        kids = _sort_nodes(kids)

        if len(kids) == 1:
            return kids[0]
        return And(tuple(kids))
    if isinstance(n, Or):
        kids = []
        for c in n.children:
            c = _normalize_tree(c)
            if isinstance(c, Or):
                kids.extend(c.children)
            else:
                kids.append(c)
        kids = _sort_nodes(kids)
        if len(kids) == 1:
            return kids[0]
        return Or(tuple(kids))
    raise TypeError


def _sort_nodes(nodes: List[Node]) -> List[Node]:
    def key(n: Node):
        if isinstance(n, Const):
            return (0, 0 if n.value else 1, '')
        if isinstance(n, Var):
            return (1, 0, n.name)
        if isinstance(n, Not):
            return (2, 0, node_to_str(n))
        if isinstance(n, And):
            return (3, len(n.children), node_to_str(n))
        if isinstance(n, Or):
            return (4, len(n.children), node_to_str(n))
        return (9, 0, '')
    return sorted(nodes, key=key)



def structurally_equal(a: Node, b: Node) -> bool:
    return a == b


def negate(n: Node) -> Node:
    return Not(n)




def factors_and(n: Node) -> Tuple[Node, ...]:
    if isinstance(n, And):
        return n.children
    return (n,)

def factors_or(n: Node) -> Tuple[Node, ...]:
    if isinstance(n, Or):
        return n.children
    return (n,)



LAW_IDEMP = "Idempotencia"
LAW_NULL = "Anulación"
LAW_IDENT = "Identidad"
LAW_COMP = "Complementario"
LAW_ABS = "Absorción"
LAW_DNEG = "Doble negación"
LAW_FACT = "Organización (factor común) – Distributiva"


def apply_rules_in_order(n: Node) -> Tuple[Node, bool, Optional[str]]:

    if isinstance(n, Not):
        child, changed, law = apply_rules_in_order(n.child)
        if changed:
            return Not(child), True, law
        # Doble negación !!X = X
        if isinstance(child, Not):
            return child.child, True, LAW_DNEG
        return n, False, None

    if isinstance(n, And):

        new_children = []
        for c in n.children:
            c2, changed, law = apply_rules_in_order(c)
            if changed:
                new = _normalize_tree(And(tuple(new_children + [c2] + list(n.children[len(new_children)+1:]))))
                return new, True, law
            new_children.append(c2)

        uniq = _unique_nodes(new_children)
        if len(uniq) < len(new_children):
            return _normalize_tree(And(tuple(uniq))), True, LAW_IDEMP

        if any(isinstance(c, Const) and not c.value for c in new_children):
            return Const(False), True, LAW_NULL

        nc = [c for c in new_children if not (isinstance(c, Const) and c.value)]
        if len(nc) < len(new_children):
            if not nc:
                return Const(True), True, LAW_IDENT
            return _normalize_tree(And(tuple(nc))) if len(nc) > 1 else nc[0], True, LAW_IDENT

        if _has_complement_pair(new_children):
            return Const(False), True, LAW_COMP

        for c in new_children:
            if isinstance(c, Or):
                for x in new_children:
                    if x is c:
                        continue
                    if x in c.children:

                        return x, True, LAW_ABS

        factored = _factor_common_for_and(new_children)
        if factored is not None:
            return factored, True, LAW_FACT
        return And(tuple(new_children)), False, None

    if isinstance(n, Or):

        new_children = []
        for c in n.children:
            c2, changed, law = apply_rules_in_order(c)
            if changed:
                new = _normalize_tree(Or(tuple(new_children + [c2] + list(n.children[len(new_children)+1:]))))
                return new, True, law
            new_children.append(c2)

        uniq = _unique_nodes(new_children)
        if len(uniq) < len(new_children):
            return _normalize_tree(Or(tuple(uniq))), True, LAW_IDEMP

        if any(isinstance(c, Const) and c.value for c in new_children):
            return Const(True), True, LAW_NULL

        nc = [c for c in new_children if not (isinstance(c, Const) and not c.value)]
        if len(nc) < len(new_children):
            if not nc:
                return Const(False), True, LAW_IDENT
            return _normalize_tree(Or(tuple(nc))) if len(nc) > 1 else nc[0], True, LAW_IDENT

        if _has_complement_pair(new_children):
            return Const(True), True, LAW_COMP

        for c in new_children:
            if isinstance(c, And):
                for x in new_children:
                    if x is c:
                        continue
                    if x in c.children:
                        return x, True, LAW_ABS
        factored = _factor_common_for_or(new_children)
        if factored is not None:
            return factored, True, LAW_FACT
        return Or(tuple(new_children)), False, None

    return n, False, None


def _unique_nodes(nodes: List[Node]) -> List[Node]:
    seen = set()
    out = []
    for n in nodes:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _has_complement_pair(nodes: List[Node]) -> bool:
    s = set(nodes)
    for n in nodes:
        if Not(n) in s:
            return True
        if isinstance(n, Not) and n.child in s:
            return True
    return False


def _intersect(a: Tuple[Node, ...], b: Tuple[Node, ...]) -> Set[Node]:
    return set(a).intersection(set(b))


def _remove_factors(src: Tuple[Node, ...], rem: Set[Node]) -> Tuple[Node, ...]:
    return tuple(x for x in src if x not in rem)


def _factor_common_for_or(children: List[Node]) -> Optional[Node]:

    and_terms = [c for c in children if isinstance(c, And)]
    if len(and_terms) < 2:
        return None
    common: Optional[Set[Node]] = None
    for t in and_terms:
        s = set(factors_and(t))
        common = s if common is None else (common & s)
        if not common:
            return None
    common_factors = tuple(sorted(common, key=lambda n: node_to_str(n)))
    if not common_factors:
        return None
    rest_terms = []
    for t in children:
        if isinstance(t, And):
            rest = _remove_factors(factors_and(t), set(common_factors))
            rest_terms.append(_normalize_tree(And(rest)) if len(rest) > 1 else (rest[0] if rest else Const(True)))
        else:
            return None
    inner = _normalize_tree(Or(tuple(rest_terms)))
    outer = _normalize_tree(And(tuple(common_factors + (inner,))))
    return outer


def _factor_common_for_and(children: List[Node]) -> Optional[Node]:
    or_terms = [c for c in children if isinstance(c, Or)]
    if len(or_terms) < 2:
        return None
    common: Optional[Set[Node]] = None
    for t in or_terms:
        s = set(factors_or(t))
        common = s if common is None else (common & s)
        if not common:
            return None
    common_factors = tuple(sorted(common, key=lambda n: node_to_str(n)))
    if not common_factors:
        return None
    rest_terms = []
    for t in children:
        if isinstance(t, Or):
            rest = _remove_factors(factors_or(t), set(common_factors))
            rest_terms.append(_normalize_tree(Or(rest)) if len(rest) > 1 else (rest[0] if rest else Const(False)))
        else:
            return None
    inner = _normalize_tree(And(tuple(rest_terms)))
    outer = _normalize_tree(Or(tuple(common_factors + (inner,))))
    return outer

def simplify_expression(expr: str) -> Tuple[str, List[dict]]:

    original = expr
    s = normalize_symbols(expr)
    ast = parse_expression(s)
    steps: List[dict] = []

    while True:
        before = node_to_str(ast)
        new_ast, changed, law = apply_rules_in_order(ast)
        if not changed:
            break
        ast = _normalize_tree(new_ast)
        after = node_to_str(ast)
        steps.append({"before": before, "law": law or "(sin cambio)", "after": after})

    return node_to_str(ast), steps

